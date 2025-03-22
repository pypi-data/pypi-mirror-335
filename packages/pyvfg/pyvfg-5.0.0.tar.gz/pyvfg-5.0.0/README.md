# pyvfg

Declares and defines a class `VFG` that represents a Verses Factor Graph.

Each file, `vfg_0_2_0` or `vfg_0_4_0`, represents a different version for import. This is necessary to load older
versions of the VFG into the current runtime.

This package should be kept as light as possible, as its role is to allow for common Python type usage, including
accessory functions, for all consumers, including the SDK.
