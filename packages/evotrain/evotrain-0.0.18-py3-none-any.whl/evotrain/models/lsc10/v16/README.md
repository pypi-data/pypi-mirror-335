
## Current LSC annotation:
- 1: tree
- 2: shrub
- 3: herbaceous vegetation
- 4: mangrove
- 5: built-up
- 6: bare
- 7: snow
- 8: water
- 9: herbaceous wetland
- 10: lichen
- 11: thick clouds
- 12: thin clouds
- 13: shadow
- 255: no data

## New annotations

land cover / physical surface cover classes
- 0: tree
- 1: shrub
- 2: herbaceous vegetation
- 3: not vegetated
- 4: water

2 tensors with shape probs=(5, y, x), weight=(1, y, x)

surface occlusion
- 0: snow
- 1: thick clouds / thin clouds
- 2: shadow
- 3: surface

thin_clouds_surface_prob = 0.3
shadow_surface_prob = 0.3

when we have a thin cloud or a shadow -> 30% on surface.

2 tensors with shape probs=(4, y, x), weight=(1, y, x)

ecosystems
- 0: cropland
- 1: mangrove
- 2: built-up
- 3: herbaceous wetland
- 4: lichens
- 5: other/natural

## Examples

Tree pixel

t 0  0
0 tc 0
0 0  c

cover
1 0   0
0 0.3 0
0 0   0

ecosystems
1 0   0
0 0.3 0
0 0   0

Mangrove pixel

m 0  0
0 tc 0
0 0  c

cover
0 0   0
0 0.5 0
0 0   0

ecosystems
1 0   0
0 0.5 0
0 0   0


the probability of the cover layer is given by the annual annotation for the cover classes
in case we have clouds and shadow

if it's thin cloud/shadow, we have 0.3 weight on the cover layer, 1 on the occlusion layer, 0.3 on the ecosystem layer
if it's thick cloud, we have 0 weight on the cover layer, 1 on the occlusion layer, 0 on the ecosystem layer but we still
put the labels probabilities in the cover layer and ecosystems so we can also test later.

once we have the probs and weights, we load every sample and compute the weighted men of the probs for each labels
group to get the labels weights (inverse of the weighted class frequency).


2 tensors with shape probs=(6, y, x), weight=(1, y, x)


one sample y has shape (14, y, x)
one sample y_weight

0-4: surface cover SC
5-7: surface occlusion SO
8-13: ecosystems EC

sum(SC) + sum(SO) = 1


y_weight is tensor with shape (batch_size, 14, y, x)

"""
loss_surface: MSE loss on surface cover classes
loss_occlusion: MSE loss on surface occlusion classes
loss_ecosystem: MSE loss on ecosystem classes

load target surface. target_surface = target_surface * (1 - target_occlusion.sum(axis=0))
loss_surface can contain loss occlusion classes.

target_ecosystems = target_ecosystems * (1 - target_occlusion.sum(axis=0))
loss_ecosystem can contain loss occlusion classes.

we use softmax2d activation...
since occlusion classes are shared in both losses, we need to first run the softmax2d 
on the sc and oc classes together, then run a custom softmax2d on the ec classes only,
taking into account the occlusion classes sum.

if annual:
- cropland: ec target 1, sc 
"""