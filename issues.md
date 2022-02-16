# Issues
## Model 1
- [ ] Should we restrict training data to the 23 species identifies, or take all species? An occurrence of a species outside of the 23 specified would be useful as a pseudo-absence occurrence. I'm thinking this may not be necessary for model 1, given the 


## Model 3
- [ ] Since this is meant to be of moderate coarseness, we should use the elevation data (as that has the second most coarse spatial resolution of 30m). Otherwise we would have to downsample the sentinel-2 data as this is 10m.

## Model 2
- [ ] Should we balance the classes for them, or leave it up to them? Currently we are up-sampling which is probably the most basic way to address the issue, there is certainly more room for creativity to better solve the problem.



## Jodie Questions

### 1. Level 1 species
For model level 1, we want it to focus on creating a species distribution model on just one Australian species. Right now, we have picked litoria fallax. For demonstration purposes, we have restricted the analysis to the Greater Sydney region, but there will be no formal limitation on what regions participants can pick to curate their training set. This region allows us to use occurrences of crinia signifera as pseudo-absence points in the demonstration. 

**Is there another species that may be of greater utility to model?**

Here are the three species I have had in mind and my thoughts on each.

| Species  | Advantages  | Disadvantages  |
| ------------ | ------------ | ------------ |
| litoria fallax  | cute, common (~36,000 obs), habitats overlap with others  |  SDM may not be useful for conservation efforts |
| austrochaperina pluvialis  | also cute, shares some habitat with litoria fallax, SDM might have greater utility (threatened)  | quite uncommon (~400 obs), endemic to NQLD - coarse spatial res of TerraClimate may struggle|
| crinia signifera  | very common (~97,000 obs),  habitats overlap with others  | quite ugly,  SDM may not have great utility for conservation efforts |


### 2. Test regions
Because of the size of the satellite data used in the challenges, we need to restrict the test data to a set of reasonably sized regions. The number of regions is not the main concern (although the more we have, the longer each submission will take), but the crucial thing is to limit each region to about 50km by 50km. If the region is too large, then the data will be too difficult to load in for students with limited computing resources. 

When we begin curating the test data, we will need to choose several regions from each country that contain occurrences that are representative of each species and their habitats. These decisions will have to be made by looking at the private data. If the private data is not representative enough, we have the option of blocking out regions in the training set and withholding those points for our own testing.

**Which ~50km by ~50km regions across each country would best represent each species for testing?**

We would appreciate your assistance in choosing these test regions so that they are representative of the habitats of each species. 






