## <a name="download"> Downloading a dataset from a configured repository </a> ##

To download a dataset, you need to be in an initialized and configured ml-git project. If you have a repository with your saved settings, you can run the following command to set up your environment:

```
$ ml-git clone git@github.com:example/your-mlgit-repository.git
```

With the tag of the version you want to download is rather simple to retrieve a specific version locally to start any experiment by executing one of the following commands:

```
$ ml-git datasets checkout computer-vision__images__faces__fddb__1
```

or 

```
$ ml-git datasets checkout fddb --version=1
```


If you want to get the latest available version of an entity you can just pass its name in the checkout command, as shown below:

```
$ ml-git datasets checkout fddb
```

Now your directory should look like this:

```
computer-vision/
└── images
    └── faces
        └── fddb
            ├── README.md
            ├── data
            │   ├── 2002
            │   └── 2003
            └── fddb.spec
```