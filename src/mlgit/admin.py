"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.config import mlgit_config_load, mlgit_config_save
from mlgit._metadata import MetadataManager
import os

# define initial ml-git project structure
# ml-root/
# ├── .ml-git/config.yaml 	# describe experiments (dev, test, prod) ;
# |		       		# override some specification in spec files of ml types
# | 				# describe git repository (dataset, labels, nn-params, models)
# | 				# describe settings for actual S3/IPFS storage of dataset(s), model(s)
def init_mlgit():
	try:
		os.mkdir(".ml-git")
		mlgit_config_save()
	except FileExistsError as e:
		return

# Initialize metadata & data tree structures
#
# ml-root/
# ├── .ml-git/config.yaml 	# describe experiments (dev, test, prod) ;
# ├── dataset/
# |   ├── .git
# |   ├── imaging/
# |   |   ├── receipts/
# |   |   |   ├── dataset.md 	# metadata describing the dataset
# |   |   |   └── manifest.yaml	# manifest desfcribing the data composing that version of the dataset
# |   ├── data-category/
# |   |   ├── [data-subcategory/]*
# |   ...
# ├── labels/
# |   ├── .git
# |   ├── vision-computing/
# |   |   ├── document-classification/
# |   |   |   ├── labels.md 	# metadata describing the labels
# |   |   |   └── manifest.yaml	# manifest describing the labels for the identified version of the dataset(s)
# |   ├── labels-category/
# |   |   ├── [labels-subcategory/]*
# |   ...
# ├── nn-params/
# |   ├── .git
# |   ├── vision-computing/
# |   |   ├── document-classification/
# |   |   |   ├── nn-params.md 	# metadata describing the nn-params
# |   |   |   ├── <nn arch> 	# file describing the architecture of the neural network (maybe whatever ML framework)
# |   |   |   ├── transform.dtl	# data language (DSL) describing the transformation to be operated on top of the dataset
# |   |   |   └── pos-train.yaml 	# contains description of operations to be performed after the training
# |   ├── nnparams-category/
# |   |   ├── [nnparams-subcategory/]*
# |   ...
# ├── models/
# |   ├── .git
# |   ├── vision-computing/
# |   |   ├── document-classification/
# |   |   |   ├── model.md 	# metadata describing the model & hyper parameters used for the ml experiment (including random seed, etc...)
# |   |   |   └── manifest.yaml 	# contains description of file(s) composing the model and where these are stored. (S3, IPFS, Other)
# |   ├── model-category/
# |   |   ├── [model-subcategory/]*
# |   ...
# └── data/
#     ├── dataset   # local copy of existing data already committed to S3,IPFS and (optionally) new data to push data to S3,IPFS
#     ├── augmented # augmented data will be stored here locally
#     └── models  # copy of existing models or new model to push to S3,IPFS
def init_repos():
	config = mlgit_config_load()
	#rs = [ "model", "dataset", "labels", "model" ]
	rs = [ "dataset", "labels" ]
	for r in rs:
		# first initialize metadata
		try:
			m = MetadataManager(config, type=r)
		except Exception as e:
			print(e)
			continue
		if m.check_exists() == False:
			m.init()
		# then initializes data store
		os.makedirs(config[r]["data"], exist_ok=True)

def show_config():
	for repo in list_repos():
		print("  ** %s" % (repo))
		config = repo_config(repo)
		for elt in config:
			print("     - %s" % (elt))
			for item in config[elt]:
				print("\t %s : %s" % (item, config[elt][item]))