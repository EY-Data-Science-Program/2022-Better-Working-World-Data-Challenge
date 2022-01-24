# Issues
## Model 1
- [ ] Should we restrict training data to the 23 species identifies, or take all species? An occurrence of a species outside of the 23 specified would be useful as a pseudo-absence occurrence. I'm thinking this may not be necessary for model 1, given the 


## Model 2
- [ ] Since this is meant to be of moderate coarseness, we should use the elevation data (as that has the second most coarse spatial resolution of 30m). Otherwise we would have to downsample the sentinel-2 data as this is 10m.

## Model 3
- [ ] Should we balance the classes for them, or leave it up to them? Currently we are up-sampling which is probably the most basic way to address the issue, there is certainly more room for creativity to better solve the problem.