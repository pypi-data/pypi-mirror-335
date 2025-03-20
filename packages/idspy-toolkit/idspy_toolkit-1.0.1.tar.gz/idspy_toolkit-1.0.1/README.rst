IDSPy Toolkit
=============

This module contains a serie of function to help mange and manipulate IDSPy dataclasses

 * fill_missing_values
 * ids_to_hdf5
 * hdf5_to_ids
 * get_ids_value_from_string
 * set_ids_value_from_string
 * list_ids_members
 * copy_ids


**Please note that this work is still under progress/heavy development and as experimental status.
This means that functions arguments/signatures as long as HDF5 structure might be totally redesigned in the next updates.**

## Quick example
#################################################################################################

.. code-block:: python
   :number-lines:

    import pprint
    import dataclasses

    import idspy_toolkit
    from idspy_dictionaries import ids_gyrokinetics_local as gkids

    pp = pprint.PrettyPrinter(indent=2)

    ids_test = gkids.GyrokineticsLocal()
    # you can directly print the class to see what it looks like  :
    pp.pprint(ids_test)

    # if you want to see all the available classes in the current module :
    ids_dict = idspy_toolkit.list_ids_members(gkids)
    pp.pprint(ids_dict)

    #to fill an IDS with default values following IMAS standard
    idspy_toolkit.fill_missing_values(ids_test)

    # you can use the . to access ids members :
    pp.pprint(ids_test.ids_properties)

    # and to set a value :
    ids_test.ids_properties.comment="a comment"

    # if in a script you want to reach a "deeper" value, you can use the function *get_ids_value_from_string*
    idspy_toolkit.get_ids_value_from_string(ids_test, "ids_properties/comment")
    # and for list element, put the element index after an #
    idspy_toolkit.get_ids_value_from_string(ids_test, "tag#0/name")

    # same kind of function exist to set a value :
    idspy_toolkit.set_ids_value_from_string(ids_test, "tag#0/name", "a new tag name")

    # to print the ids as a dictionary ( better with a vertical screen ;)):
    ids_dict = dataclasses.asdict(ids_test)
    pp.pprint(ids_dict)

    # HDF5 Operations Example
    # Save IDS to HDF5 file (will raise IOError if file exists)
    idspy_toolkit.ids_to_hdf5(ids_test, "my_ids.h5")

    # Save with overwrite option and array size constraints
    idspy_toolkit.ids_to_hdf5(ids_test, "my_ids.h5",
                             overwrite=True,          # Overwrite existing file
                             max_array_dim=2,         # Maximum array dimensions
                             max_array_size=100,      # Maximum size in MB
                             max_array_elements=1000) # Maximum number of elements

    # Load IDS from HDF5 file with constraints
    loaded_ids = idspy_toolkit.hdf5_to_ids("my_ids.h5", 
                                          ids_gyrokinetics.Gyrokinetics,
                                          fill=True,           # Fill missing values with defaults
                                          todict=True,         # Convert XML strings to dictionaries
                                          max_array_dim=2,     # Maximum array dimensions to load
                                          max_array_size=100,  # Maximum array size in MB
                                          max_array_elements=1000) # Maximum number of elements
