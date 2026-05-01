# Meteo 473 Winter Energy Stress Index - Group 6

# Project Description (PD and MP)
- We created a winter energy stress index based on ECMWF model data from the snowstorm in late January of 2026. We used variables such as 2m temperature, 10m wind gust, precipitation type, precipitation rate, and derived wind chill to calculate our overall index. It is based on energy demand from increased heating as well as infrastructure stress based on damage to power lines, trees, etc. Our index is based from 0-10 with 0 being no additional effects, and 10 being the most severe conditions. This is intended for utility companies, emergency management teams, and the general public to use to guage how strongly upcoming winter storms and arctic cold outbreaks will induce stress on the energy grid. Our index calculation included weighting each variable in different ways based on how effectively each variable tends to cause stress on the energy system. Precipitation type and wind chill were weighted at 27.5%, 10m wind gust was weighted at 20%, 2m temperature was weighted at 15%, and precipitation rate was weighted at 10%. 
  
# Project Members
- Matthew Pollard
- Patrick Dela Rosa

# How To Use (MP)
- The winter_threat_index.py file is the only file that needs to be run that downloads all data, calculates our index based on this data, and creates all plots for the respective time steps that are shown such as winter_threat_000.png, winter_threat_006.png, etc.
- All website functions are placed in the webfiles folder such as html, javascript, and css files.
- Milestone_1_gp6.ipynb and Milestone2_final.ipynb are the two notebooks that went through our workflow indepth to start thinking about our factors and how we actually generated and calculated our indices.
  
# License (MP)
MIT


