
Core
====
This program should replace me, or at least the interesting part of me, for the LBAI


TODO
====

# introspection module
[x] write a function to test if zscore figure is significant
[x] test check sinificant zscore function
[x] include significant zscore figures from introspection results in report
[] get signame to pathway name
[] craft a data file with all the pathway significantly different
[] include table in report
[] add mode for runner to perform only introspection on a pre existent murloc result folder
[] add mode for runner to perform only introspection on a single data file (same mode as above but catch the input type difference)

# code refactoring
[x] clean deprecated files
[x] create a directory for fs module
[] create a directory for the report module
[x] update requirements file
[x] create a clean function in murloc to clean generated test files and folders
[] drop unused function in murloc
[x] embed test run in a function in murloc
[] rework the action system, keep only test & clean & introspection and run from configuration

# rational module
## the idea is to craft a module that read the results and came with a "rational" to descriminate the groups, e.g find the biological pathway that is most discriminating
## and put it in the report, as a kind of discussion
[] read results of introspection file and associate a pathway to a signame
[] read results of introspection file and retrieved significatly different pathway
[] read results of annotation file and retrieved significatly different pathway
[] create a table with pathway name / significant differences betwwen groups and origins (direct annotation or introspection) in the final report

# report module
[x] create html report version
[] include pca in report
[x] include heatmap in report
[] add nice style to report
[] let html be the default report option (switch name function)
[] refactor html generator (put clf in a loop)

# test module
[x] create a test module
[x] create a test dataset function
[x] create a test config file
[x] create a test command
[] create "real" test dataset to test annotation function
[] write the test doc in the help function

