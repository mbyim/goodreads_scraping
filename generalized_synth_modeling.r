library(tidyverse)
library(gsynth)
library(panelView)
data <- read.csv("enhanced_book_data.csv")
data <- data %>% distinct(book_id, date, .keep_all = TRUE)
data %>% count(book_id)
data$added_and_to_read <- data$added + data$to.read
data$date <- as.Date(data$date, "%Y-%m-%d")
#manually entering ids from ft
history <- c(130758645, 62217087, 62192405, 193907194, 61282598,
            62847908, 61884887, 62121704, 75657079, 61898069, 61089447)
politics <- c(96177657, 111172404, 120532418, 75495020, 61349852,
              77920745, 199542911, 63326676, 62347050, 61327508, 61813215, 123199472, 112976346)
economics <- c(62874267, 123993293, 61898079, 122773797, 62927217,
               197693246, 188547135, 177281779, 62347058, 63933739,
               90663680, 123831773, 123436434, 62792704, 62921469, 86532647, 65211868, 75560036)

all_treated <- c(history, politics, economics)
data$treated <- data$book_id %in% all_treated #was book in treatment
data$subject <- case_when(data$origin_book_id %in% history ~ 'history',
                          data$origin_book_id %in% politics ~ 'politics',
                          data$origin_book_id %in% economics ~ 'economics')
data$post_treatment <- case_when(data$subject == 'history' & data$treated & data$date >= '2023-11-16' ~ as.integer(1),
                                 data$subject == 'politics' & data$treated & data$date >= '2023-11-17' ~ as.integer(1),
                                 data$subject == 'economics' & data$treated  & data$date >= '2023-11-15' ~ as.integer(1),
                                 TRUE ~ as.integer(0) #to avoid NAs
                                 )
                                 #pre vs post treatment dates


#Overview of groups & staggered treatment
panelview(added_and_to_read ~ post_treatment, data = data, 
          index = c("book_id", "date"), pre.post = TRUE, axis.lab.gap = 10,
          by.timing = TRUE)

#outcome view
panelview(added_and_to_read ~ post_treatment, data = data, 
          index = c("book_id", "date"), type = "outcome", 
          main = "EDR Reform and Turnout", 
          by.group = TRUE)

out <- gsynth(added_and_to_read ~ post_treatment, data = data,
              index = c("book_id", "date"), 
              se = TRUE, inference = "parametric", 
              r = c(0, 5), CV = TRUE, force = "two-way", 
              nboots = 1000, seed = 02139)

plot(out, type = "gap", xlim = c(-20, 15), ylim=c(-30,30))

plot(out, type = "raw", xlab = "Year", ylab = "'Shelved'", ylim=c(-0,500))

plot(out, type="counterfactual")

#123831773
plot(out, type = "counterfactual", id = "123831773", 
     raw = "all", legendOff = TRUE)

#now try doing the same filtering on outliers that i did in my python notebook and see if it changes anything
df_filtered <- data %>%
  group_by(book_id) %>%
  filter(all(added_and_to_read <= 200))

outfiltered <- gsynth(added_and_to_read ~ post_treatment, data = df_filtered,
              index = c("book_id", "date"), 
              se = TRUE, inference = "parametric", 
              r = c(0, 5), CV = TRUE, force = "two-way", 
              nboots = 1000, seed = 02139)

plot(outfiltered, type = "gap", xlim = c(-20, 15), ylim=c(-30,30))

plot(outfiltered, type = "raw", xlab = "Year", ylab = "'Shelved'", ylim=c(-0,500))
plot(outfiltered, type = "counterfactual", id = "123831773", 
     raw = "all", legendOff = TRUE, xlab.gap = 10)
plot(outfiltered, type = "gap", id = "123831773", 
      legendOff = TRUE)
