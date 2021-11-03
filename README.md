# Updating the image #
docker rm adv_decl
docker rmi valyo/adv_decl
# copy the new python file into src/
docker build -t valyo/adv_decl .
docker push valyo/adv_decl

# Running the app with docker-compose #
DRYRUN=dry docker-compose up 	# for dry run
or 
docker-compose up 				# for production
