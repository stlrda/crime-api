# Extract SLMPD Monthly Crime Releases
#
# Dependencies:
library(compstatr)
library(DBI)
library(RPostgres)
library(sf)
library(dplyr)
library(magrittr)
library(pushoverr)
library(lubridate)

# Connect to Database
con <- DBI::dbConnect(
  RPostgres::Postgres(),
  dbname = Sys.getenv('DB_NAME'),
  host = Sys.getenv('DB_HOST'),
  port = Sys.getenv('DB_PORT'),
  user = Sys.getenv('USER'),
  password = Sys.getenv('PASS')
)

# Optionally Auth Pushover
if(Sys.getenv('pushover') != ''){
  creds <- unlist(strsplit(Sys.getenv('pushover'), ':', fixed = TRUE))
  set_pushover_user(user = creds[1])
  set_pushover_app(token = creds[2])
}

##########################################
######## Define CS Scrape Methods ########
# (Full and Append) and Cleaning Process #
##########################################

cs_clean <- function(crime_data){
  # Create SF Object to Reproject Coordinates
  # (> 300 is arbitrary for bad geocodes)
  sf <-
    select(crime_data, id, x_coord, y_coord) %>%
    mutate_all(as.numeric) %>%
    filter(x_coord > 300 & y_coord != 0) %>%
    st_as_sf(coords = c("x_coord", "y_coord"),
             crs = "+proj=tmerc +lat_0=35.83333333333334 +lon_0=-90.5 +k=0.9999333333333333 +x_0=250000 +y_0=0 +datum=NAD83 +units=us-ft +no_defs") %>%
    st_transform(crs = 4326)
  
  sf %<>%
    mutate(
      wgs_x = st_coordinates(sf)[,1],
      wgs_y = st_coordinates(sf)[,2]
    ) %>%
    st_drop_geometry
  
  # Join New Coordinates
  crime_data %<>% left_join(sf, by = "id")
  
  # Add Names to Crime Codes
  crime_data %<>%
    mutate(
      crime = as.numeric(crime),
      ucr_category = case_when(
        between(crime, 10000, 19999) ~ "Homicide",
        between(crime, 20000, 29999) ~ "Rape",
        between(crime, 30000, 39999) ~ "Robbery",
        between(crime, 40000, 49999) ~ "Aggravated Assault",
        between(crime, 50000, 59999) ~ "Burglary",
        between(crime, 60000, 69999) ~ "Larceny",
        between(crime, 70000, 79999) ~ "Vehicle Theft",
        between(crime, 80000, 89999) ~ "Arson",
        between(crime, 90000, 99999) ~ "Simple Assault",
        between(crime, 100000, 109999) ~ "Forgery",
        between(crime, 110000, 119999) ~ "Fraud",
        between(crime, 120000, 129999) ~ "Embezzlement",
        between(crime, 130000, 139999) ~ "Stolen Property",
        between(crime, 140000, 149999) ~ "Destruction of Property",
        between(crime, 150000, 159999) ~ "Weapons Offense",
        between(crime, 170000, 179999) ~ "Sex Offense",
        between(crime, 180000, 189999) ~ "VMCSL",
        between(crime, 200000, 209999) ~ "Offense Against Family",
        between(crime, 210000, 219999) ~ "DWI/DUI",
        between(crime, 220000, 229999) ~ "Liquor Laws",
        between(crime, 240000, 249999) ~ "Disorderly Conduct",
        between(crime, 250000, 259999) ~ "Loitering/Begging",
        TRUE ~ "Other"
      ),
      gun_crime = ifelse(
        (crime > 41000 & crime < 42000) | 
          crime %in% c(31111, 31112,32111,32112,33111,34111,
                       35111,35112,36112,37111,37112,38111,38112),
        TRUE,FALSE
      ),
      time_occur = hms::as_hms(lubridate::mdy_hm(date_occur)),
      date_occur = as.Date(lubridate::mdy_hm(date_occur))
    )
  
  # Fit to Specific Database Schema
  schema <- crime_data %>%
    transmute(
      id = as.integer(id),
      date = as.Date(date_occur),
      time = time_occur,
      flag_crime = as.logical(if_else(flag_crime == 'Y', TRUE, FALSE, missing = FALSE)),
      flag_unfounded = as.logical(if_else(flag_unfounded == 'Y', TRUE, FALSE, missing = FALSE)),
      flag_admin = as.logical(if_else(flag_administrative == 'Y', TRUE, FALSE, missing = FALSE)),
      count = as.logical(if_else(count == 1, TRUE, FALSE)),
      code = as.integer(crime),
      category = as.character(ucr_category),
      district = as.integer(district),
      description = as.character(description),
      neighborhood = as.integer(neighborhood),
      lon = as.numeric(wgs_x),
      lat = as.numeric(wgs_y)
    )
  
  return(schema)
}

cs_full_build <- function(con){
  tryCatch({
    # Create Index of Available Data and Get Latest Date
    idx <- cs_create_index()
    latest_crime <- cs_last_update('date')
    
    # Define Range of Years and Iterate
    years <- 2008:as.numeric(format(latest_crime, '%Y'))
    crime_data <- lapply(years, function(x) cs_get_data(x, index = idx))
    
    ## Fix outliers (Standardize to 20 Columns)
    # 2008-2012: 18 Column Release
    # 2013 Jan - May, July, Aug: 18 Column Release
    # (Method 'All' Doesn't Have Unintended Consequences)
    for (i in 1:6) {
      crime_data[[i]] %<>% cs_standardize('all', config = 18)
    }
    
    # 2017 May: 26 Column Release
    crime_data[[10]] %<>% cs_standardize("May", config = 26)
    
    # Build Full Dataset by Binding Rows
    crime_data %<>%
      lapply(bind_rows) %>%
      bind_rows
    
    # Add Unique ID For Each Row in Dataset
    crime_data %<>% mutate(id = row_number())
    
    schema <- cs_clean(crime_data)
    
    # Write Crime Table
    dbWriteTable(con, 'crime', schema, overwrite = TRUE)
    # Write Update Table
    dbWriteTable(con, 'update',
                 data.frame(
                   stringsAsFactors = FALSE,
                   crime_last_update = as.Date(latest_crime)
                 ),
                 overwrite = TRUE
    )
  }, error = function(e){
    pushover(title = 'Unspecified Error in Scraping Crime Data', e$message)
    stop('Unspecified Error in Scraping')
  })
  # Send Notification and Terminate
  pushover(title = 'Crime Extractor Success', 'The Entire Database Has Been Created')
  stop('Scrape Completed Successfully')
}

cs_append <- function(con){
  tryCatch({
    # Create Index of Available Data and Get Latest Date
    idx <- cs_create_index()
    latest_crime <- cs_last_update('date')
    
    # Get Latest Data
    latest_crime_data <- cs_get_data(
      as.numeric(format(latest_crime, '%Y')),
      as.numeric(format(latest_crime, '%m')),
      index = idx
    )
    
    # Get Latest ID from Database (NEED TO VERIFY)
    offset <- DBI::dbGetQuery(con, "SELECT MAX(id) FROM crime;")$max
    
    # Offset Unique IDs by this Value
    latest_crime_data %<>% mutate(id = row_number() + offset)
    
    schema <- cs_clean(latest_crime_data)
    
    # Append to Crime Table
    dbAppendTable(con, 'crime', schema)
    # Write Update Table
    dbWriteTable(con, 'update',
                 data.frame(
                   stringsAsFactors = FALSE,
                   crime_last_update = as.Date(latest_crime)
                 ),
                 overwrite = TRUE
    )
    
  }, error = function(e){
    pushover(title = 'Unspecified Error in Scraping Crime Data', e$message)
    stop('Unspecified Error in Scraping')
  })
  # Send Notification and Terminate
  pushover(title = 'Crime Extractor Success', 'The Most Recent Month Has Been Appended')
  stop('Scrape Completed Successfully')
}

######################
# Logic for Updating #
######################

# Check What Tables Exist
tables <- dbListTables(con)
crime_exists <- 'crime' %in% tables
update_exists <- 'update' %in% tables
no_tables <- !crime_exists & !update_exists

# Notify if Only One Exists
if(sum(crime_exists, update_exists) == 1){
  pushover(title = 'Error in Crime Extractor', 
           paste(sep = '\n', 'A Table Does Not Exist',
                 'Crime Exists:', crime_exists,
                 'Update Exists:', update_exists
           )
  )
  stop('Error in Table Existence')
}

# Neither Table Exists
if(no_tables){
  cs_full_build(con)
}else{
  # Check Latest Update (For New Data)
  db_latest <- dbReadTable(con, 'update')$crime_last_update
  cs_latest <- cs_last_update('date')
  new_data <- db_latest < cs_latest
}
if(new_data){
  cs_append(con)
}else{# Nothing
  stop('Terminating. No Updates Found')
}