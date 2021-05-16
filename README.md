# Downdetector Exporter


## Metrics

| Name | Description |
|---|---|
| downdetector_status | Shows if downdetector consider the service down. |
| downdetector_max_baseline |Max baseline for Downdetector|
| downdetector_max_baseline |Min baseline for Downdetector|
| downdetector_informs |Informs received from Downdetector.|
| downdetector_baseline | Current baseline received from Downdetector. |

## Usage

Copy .env.dist -> .env, set your url and execute `docker-compose up -d`.
