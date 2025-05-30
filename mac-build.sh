echo "[INFO] Building Docker image..."

docker buildx build --platform linux/amd64 -t robots:latest \
  --output type=docker,dest=robots.tar .

echo "[INFO] Converting Docker image to SIF..."

docker run --rm \
  --privileged \
  -v "$(pwd)":/workspace \
  -w /workspace \
  ghcr.io/apptainer/apptainer \
  apptainer build --arch amd64 --force robots.sif oci-archive://robots.tar

echo "[INFO] Copying to cluster"
scp ./robots.sif jlis@hpc.itu.dk:/home/jlis/robots2.sif
echo "[INFO] Done."
