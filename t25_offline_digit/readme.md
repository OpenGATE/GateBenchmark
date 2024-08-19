


## Example 1

Simple Cylindrical PET with 20 x 20 block, 5x5 crystal, LSO and BGO layer, 4 rings. 
- No phantom.
- Physics list: emstandard_opt4
- Digitizer: adder, NO readout, threshold, coinc 10 ns
- Source: back to back 511 keV, half-life of 1223 sec (C11)

```shell
Gate mac/main2.mac
```
This will generate ```output/output1.root``` with all hits only.


```shell
GateDigit_hits_digitizer output/output1.root output/output1-singles.root mac/main1_offline_digitizer.mac
```
This will generate ```output/output1-singles.root``` with the singles.


```shell
GateDigit_singles_sorter output/output1-singles.root output/output1-coinc.root mac/main1_offline_sorter.mac abs
```
This will generate ```output/output1-coinc.root``` with the singles.




## Example 2

