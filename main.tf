// Configure the Google Cloud provider
provider "google" {
 credentials = "${file("credenciales.json")}"
 project     = "x-pivot-241800"
 region      = "us-west1"
}

// Terraform plugin for creating random ids
resource "random_id" "instance_id" {
 byte_length = 8
}

// A single Google Cloud Engine instance
resource "google_compute_instance" "default" {
 name         = "flask-vm-${random_id.instance_id.hex}"
 machine_type = "n1-standard-8"
 zone         = "us-west1-a"

 boot_disk {
   initialize_params {
     image = "ubuntu-os-cloud/ubuntu-1804-lts"
   }
 }

// Make sure flask is installed on all new instances for later steps
 metadata_startup_script = "sudo apt-get update; sudo apt-get install -yq build-essential python-pip rsync; pip install flask"

 network_interface {
   network = "default"

   access_config {
     // Include this section to give the VM an external ip address
   }
 }
 metadata {
   sshKeys = "matias:${file("~/.ssh/id_rsa.pub")}"
 }
}
resource "google_compute_firewall" "default" {
 name    = "flask-app-firewall"
 network = "default"

 allow {
   protocol = "tcp"
   ports    = ["5000"]
 }
}
// A variable for extracting the external ip of the instance
output "ip" {
 value = "${google_compute_instance.default.network_interface.0.access_config.0.nat_ip}"
}

resource "google_bigquery_dataset" "default" {
  dataset_id                  = "Dataset_1"
  friendly_name               = "test"
  description                 = "Dataset de prueba"
  location                    = "EU"

  labels = {
    env = "default"
  }
}

resource "google_bigquery_table" "default" {
  dataset_id = "${google_bigquery_dataset.default.dataset_id}"
  table_id   = "Personas"

  time_partitioning {
    type = "DAY"
  }

  labels = {
    env = "default"
  }

  schema = "${file("schema.json")}"
}