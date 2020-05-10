* * * * * python3 /home/pi/export_scraped_file_size.py -e jl -d /home/pi/repos/art_docker/data/ -o /home/pi/metrics/file_sizes.prom.$$ && mv /home/pi/metrics/file_sizes.prom.$$ /node_exporter/textfile_collector/file_sizes.prom
7 4 * * * python3 /home/pi/start_spiders.py -run arbejderen_frontpage
7 5 * * * python3 /home/pi/start_spiders.py -run finans_frontpage
5 6 * * * python3 /home/pi/start_spiders.py -run kristeligt_frontpage
4 7 * * * python3 /home/pi/start_spiders.py -run dr_frontpage
2 8 * * * python3 /home/pi/start_spiders.py -run bt_frontpage
