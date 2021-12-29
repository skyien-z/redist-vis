# redist-vis

## Intro
Political Redistricting is the process of drawing electoral district maps; the citizens of each district elect their district representatives. In order to account for population shifts, districts are redrawn at least every ten years. However, there is much controversy surrounding political redistricting because the way that districts are drawn can favor one political party over the other (a district plan that is drawn to give one party an advantage over another is known as a gerrymandered district plan). As an attempt to remedy this problem, the Supreme Court has established that the court system can hear cases of potential gerrymandering and mark district plans as unconstitutional if gerrymandering is proven. However, gerrymandering is very hard to prove by simply looking at a district map, so researchers have recently looked toward quantifying district plan “fairness” through using computer algorithms to generate a large number of potential district plans and calculating the relative equity between them. This equity is measured through metrics development by political scientists; we will explain some of these metrics in more depth later. 

##Aim
We have created an interactive mapping of 83 distinct district plans (each district plan one unit different from the one before and after it) and calculated some “fairness” metrics for each district plan in order to better visualize the concept of political redistricting. Traditionally, the courts have held that if one district plan has “fairness” metrics that vary significantly from the “fairness” metrics of the majority of potential district plans, it is a biased (and therefore gerrymandered) plan that needs to be altered.


##Metric Descriptions:
###Efficiency Gap
The efficiency gap measures discrepancies in wasted votes between parties as a metric to detect gerrymandering. Wasted votes are either votes that are either given to a candidate who loses the election or votes given to the victor above the amount needed to secure the election. A high-magnitude efficiency gap can indicate a gerrymandered district map as one party wastes more votes than the other. In other words, their use of votes to win seats is less efficient.  

###Mean-median gap
As the name suggests, the mean-median gap is the difference between the mean of a party's vote share and its median vote share across all the districts in a plan. We report the mean-median gap from the Republican perspective. A high mean-median gap can be an indication of a gerrymandered district plan as it indicates a skew in favor of one party over the other.

###Sainte-Lague Index of Disproportionality
The Sainte-Lague Index measures the difference in proportion between the seat share and vote share of a party. A party’s seat-share refers to the proportion of seats a party got out of the total number of seats, and a party’s vote-share refers to the proportion of votes a party got out of the total number of votes cast. Ideally, these two proportions should be equal or close to equal. This means that generally the lower the Sainte-Lague index, the better. It is also worth noting that there are many methods for computing this disproportionality, but according to Trinity College Political Science Professor, Michael Gallagher, in the paper Proportionality, disproportionality and electoral systems, the Sainte-Lague method is theoretically “probably the soundest of all measures.”


[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/skyien-z/redist-vis/slider_with_aggregate_districts.py)
