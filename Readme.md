# Roided Holehe OSINT

This is Roided Holehe OSINT. A python program that runs on top of Holehe OSINT. Roided Holehe allows you to check multiple emails existence in multiple websites. For further information about Holehe check https://github.com/megadose/holehe.

Author: Ishfaq Ahmed
Based On: Holehe by megadose

## How to use:

1.  Run app.exe in 'dist/app'.
2.  Copy the path to your file and paste it when the program asks for the file. The input file should contain the emails on a column with a header and the file type be .xlsx.
3.  Only the valid emails from the column will be processed so you don't need to check for invalid values.
4.  Once the program ends, the file will be saved to a folder "RoidedHolehe" in your documents folder.
5.  If the results have too many rate_limit as 'true' then change your ip address and re-run the program with only rate_limit='true'.
