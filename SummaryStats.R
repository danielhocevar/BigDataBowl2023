library(tidyverse)
library(dplyr)
play_data <- read_csv("C:\\Users\\barto\\Downloads\\Big Data Bowl 2023\\Data\\plays.csv")

## Number of Plays by Type
num_plays <- play_data %>%
  group_by(passResult) %>%
  summarise(n=n())

## Play by Down Function
num_plays_by_down <- function(play_choice){
  play_data %>%
  filter(passResult == play_choice) %>%
    group_by(down) %>%
    summarise(n=n())
}

## Number of Coverages by Type
num_coverages <- play_data %>%
  group_by(pff_passCoverage) %>%
  summarise(n=n())

## Coverage by Down Function
num_coverages_by_down <- function(coverage_choice){
  play_data %>%
    filter(pff_passCoverage == coverage_choice) %>%
    group_by(down) %>%
    summarise(n=n())
}


## Number of Formations by Type
num_formations <- play_data %>%
  group_by(offenseFormation) %>%
  summarise(n=n())

## Formations by Down Function
num_formations_by_down <- function(formation_choice){
  play_data %>%
    filter(offenseFormation == formation_choice) %>%
    group_by(down) %>%
    summarise(n=n())
}

## Number of Defenders in Box by Amount
num_box_defenders <- play_data %>%
  group_by(defendersInBox) %>%
  summarise(n=n())

## Formations by Down Function
num_box_defenders_by_down <- function(num_box_defenders_choice){
  play_data %>%
    filter(defendersInBox == num_box_defenders_choice) %>%
    group_by(down) %>%
    summarise(n=n())
}


## Number of Pass Coverage Types by Type
num_pass_coverages <- play_data %>%
  group_by(pff_passCoverageType) %>%
  summarise(n=n())


## Number of Pass Coverage Types by Down Function
num_pass_coverages_by_down <- function(pass_coverage_choice){
  play_data %>%
    filter(pff_passCoverageType == pass_coverage_choice) %>%
    group_by(down) %>%
    summarise(n=n())
}


## Play Result Lengths by Interval
play_result_lengths <- play_data %>%                       
  mutate(play_intervals = cut(playResult, seq(min(playResult), max(playResult), 10))) %>% 
  group_by(play_intervals) %>% 
  summarize(n=n()) %>% 
  as.data.frame()