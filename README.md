

TODO
====

# introspection module
[x] write a function to test if zscore figure is significant
[] test check sinificant zscore function
[] include significant zscore figures from introspection results in report
[] add mode for runner to perform only introspection on a pre existent murloc result folder
[] add mode for runner to perform only introspection on a single data file (same mode as above but catch the input type difference)

# code refactoring
[x] clean deprecated files
[x] create a directory for fs module
[] create a directory for the report module
[] update requirements file

# rational module
## the idea is to craft a module that read the results and came with a "rational" to descriminate the groups, e.g find the biological pathway that is most discriminating
## and put it in the report, as a kind of discussion
[] read results of introspection file and associate a pathway to a signame
[] read results of introspection file and retrieved significatly different pathway
[] read results of annotation file and retrieved significatly different pathway
[] create a table with pathway name / significant differences betwwen groups and origins (direct annotation or introspection) in the final report

# report module
[] add nice style to report

# test module
[x] create a test module
[x] create a test dataset function
[x] create a test config file
[] create a test command
[] write the test doc in the help function

