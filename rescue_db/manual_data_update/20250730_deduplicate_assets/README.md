# Goal

The code in this folder aims to drop duplicates among URLs in the table named `assets`. This is because the relationship between `assets` and `resources`
is one-to-many namely one asset has one and only one resource. But this is wrong, an asset can be found in multiple resources.

# What does the code do?

In a nutshell, the different files do the following:
- create a backup table for the `asset_resource` relationship table that will be used to populate this table after it is created by alembic, this way we keep track of the saved relationships during the DB migration
- create a backup table for the `assets` table in case something goes wrong during the DB migration
- create the `assets_deduplicated` table to store the deduplicated assets temporarily 
- truncate the `assets` table and then populate it with the data from `assets_deduplicated`

# How-to

Run the different files in the order defined in their prefix. You can run the files in the `checks` folder to check the volumetries, note that
each file is linked to the ones of the parent folder thanks to their prefix. For example, the check file `01_asset_resource_backup_volumetry.sql`
is linked to `01_create_asset_resource_backup.sql` from the parent folder of the `checks` folder.