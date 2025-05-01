echo "[INFO] Building Docker image..."
docker build -t robots .
echo "[INFO] Converting Docker image to SIF..."
apptainer build --force robots.sif docker-daemon://robots:latest
echo "[INFO] Copying to cluster"
scp ./robots.sif jlis@hpc.itu.dk:/home/jlis/
echo "[INFO] Done."
