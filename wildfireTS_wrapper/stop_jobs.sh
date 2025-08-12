
echo "Stopping PBS jobs..."
qstat -n | grep "$SHORT_USER" | awk '$5 == "R" || $5 == "Q" {print $1}' | xargs -r qdel
ssh derecho "qstat -n | grep \"krstu\" | awk '$10 == R || $10 == Q' | cut -c1-7 | xargs -r qdel" 
echo "Done!"
