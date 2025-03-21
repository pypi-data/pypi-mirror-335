.. _changelog:

###########
 Changelog
###########

This changelog describes the changes made between the different alpha versions of
|Finesse|. When seeing unexpected behavior with existing finesse scripts after updating,
you should read the entries between the last working version and the version introducing
the issues, to see if there are any entries that are relevant to your code. See
:ref:`updating_finesse` for instructions on how to update to the latest version.

.. note::

   You are currently looking at the documentation for |Finesse| |release|. Some of the
   changes listed for older versions may no longer be relevant, or contain broken links
   to non-existing documentation pages.

***************************************************
`3.0a32 <https://finesse.ifosim.org/docs/3.0a32/>`_
***************************************************

Fixed
=====
- :class:`finesse.components.modulator.Modulator` and
  :class:`finesse.components.nothing.Nothing` were not correctly handling mismatches
  changing during a simulation across their nodes which is now fixed.
- Nested :class:`finesse.solutions.array.ArraySolution`s did not work correctly as
  :class:`finesse.solutions.array.ArraySolution` memoryviews were being held on a
  workspace basis. So running a :class:`finesse.analysis.actions.axes.Noxaxis`` in a
  :class:`finesse.analysis.actions.axes.Xaxis` would conflict which memoryview was being
  used.
- Fixed not having the ``IPython`` library installed preventing you from importing
  |Finesse|
- Fixed incompatibility with new major ``IPython`` release (9.0)
- Fixed signal :ref:`modelling example <signal_example>` to use the `pwr` node instead
  of the `amp` node on the laser
- Fixed bug report functionality for python 3.13 (:ref:`reporting_issues`)
- Fixed :meth:`finesse.model.Model.plot_graph` not working in a notebook environment
- Fixed carrier simulation not being ran when running an optimizer on a
  :class:`finesse.detectors.bpdetector.BeamPropertyDetector`

Added
=====

- :ref:`MR !288<https://gitlab.com/ifosim/finesse/finesse3/-/merge_requests/288>`_ adds
  ring heater thermal deformation calculations to the thermal module. See
  :mod:`finesse.thermal.ring_heater` for more information.
- :ref:`MR !289<https://gitlab.com/ifosim/finesse/finesse3/-/merge_requests/289>`_
  allows model to be pickled for storing. Should only be used for short term storage of
  a model, as it is not guaranteed to be compatible with future versions or across
  different platforms or systems. See :ref:`serialisation_python`
- Missing katscript documentation for :ref:`alens_katscript` component

Changes
-------
- Added ``ipykernel`` as doc build dependency as that doesn't seem to get installed now
  through other dependencies and leads to the doc build complaining that python3 doesn't
  exist.

***************************************************
`3.0a31 <https://finesse.ifosim.org/docs/3.0a31/>`_
***************************************************

Added
=====

- Wheels for linux/macos 3.13

***************************************************
`3.0a30 <https://finesse.ifosim.org/docs/3.0a30/>`_
***************************************************

Added
=====

- :class:`finesse.components.lens.AstigmaticLens` element added with x and y focal
  length parameters. Works the same as a :class:`finesse.components.lens.Lens` and also
  has an OPD map attribute.
- Added simple sinusoidal and Helical LG mode calculation functions to
  :mod:`finesse.cymath.laguerre` module, see :ref:`example <hom_laguerre>`
- Added developer documentation :ref:`page <code_overview>` on the internal matrix
  solver.
- Added ``reverse_gouy`` and ``flip_lr`` options to
  :meth:`finesse.knm.map.Map.scatter_matrix` to allow for more flexibility in how the
  scatter matrix is computed.

Fixed
=====

- Fixed #685: Figure dictionary return by ``solution.plot()`` method has correct strings
  keys when single detector is present.
- Fixed #669: :meth:`finesse.knm.maps.Map.remove_piston`` accepts spot_size only with
  type ``float`` and not ``np.float``
- Fixed #666: :class:`finesse.analysis.actions.dc.DCFieldsSolution` and
  :class:`finesse.analysis.actions.lti.FrequencyResponseSolution`` cannot select
  themselves by name
- Fixed #573: Symbolic changing division in lens focal length makes cavity
  unstable
- Fixed a collection of warnings in various tests

Changed
=======

- Drop support for Python 3.9 due to various packages no longer supporting it
- Allows a superclass of :class:`finesse.knm.maps.Map` to be used as a base class for
  custom maps. This allows for more flexibility in defining custom maps that define
  their own aperture and surface functions. The following example demonstrates:

.. code:: ipython3

   class CustomMap(Map):
      def __init__(self):
         x = ...
         y = ...
         super().__init__(
            self,
            x,
            y,
            opd=self.surface,
            amplitude=self.aperture,
         )

      def aperture(self, model=None):
         return ...

      def surface(self, model=None):
         return ...

- :class:`finesse.exceptions.NotChangeableDuringSimulation`` now raised when trying to
  change a parameter that is not changeable during a simulation. This also fixes a bug
  where these changes are circumvented by using symbolics. Parameters that are not
  changeable during a simulation are flagged because some internal logic has not been
  implement yet to handle these changes.

*****************************************************
 `3.0a29 <https://finesse.ifosim.org/docs/3.0a29/>`_
*****************************************************

Fixed
=====

- Fixed a critical bug in :class:`finesse.analysis.actions.dc.DCFields` where the fields
  were not always recalculated after parameter changes.
- Fixed broken :class:`finesse.components.isolator.Isolator` component, which caused a13
  segfault in included in a model that was being run.

Added
=====

- Added a new utility function :func:`finesse.utilities.bug_report.bug_report` to make
  it easier to report issues by automatically collecting relevant information. See
  :ref:`reporting_issues` for an example.
- Added a ``show`` and ``path`` argument to :meth:`finesse.model.Model.plot_graph` to
  control whether to show the plot and whether to save it to disk.

Changed
=======

-  Use a more numerically stable method for calculating the frequency response of zpk
   filters which is more robust with filters with a large number of roots.
-  FieldDetectors now work with planewave models and no longer throw a warning.

*****************************************************
 `3.0a28 <https://finesse.ifosim.org/docs/3.0a28/>`_
*****************************************************

This release includes two changes to default way of handling phases in |Finesse|,
which are listed below. The effect of these changes is subtle, and described in
detail in :ref:`phase_configurations` and :ref:`beamsplitter_phase`.

.. warning::

   If your simulations produce different results after updating to this release, it is
   likely that your previous results were incorrect, since the old default can break
   power conservation in certain setups.

You can switch between the two settings using :meth:`finesse.model.Model.phase_config`

.. code:: ipython3

   # new default
   model.phase_config(False, True)
   # old default
   model.phase_config(True, True)

You can use this to check if your results are impacted by this change.

The changes have been tested with both the finesse-ligo_ and finesse-virgo_ packages,
so if you are using these you will probably not be affected.

If you have any questions, do not hestitate to contact us via the `matrix channel
<https://matrix.to/#/#finesse:matrix.org>`_.

.. _finesse-ligo: https://finesse.docs.ligo.org/finesse-ligo/index.html
.. _finesse-virgo: https://git.ligo.org/finesse/finesse-virgo


Breaking Changes
================

-  The default value for ``zero_k00`` :meth:`finesse.model.Model.phase_config` has been
   changed to ``False``. See :ref:`phase_configurations` for more information and an
   example of how the old default can break power conservation in the simulation Any
   simulation running with higher order modes and a cavity could be affected by this
   change and users using :class:`finesse.knm.maps.Map` should make sure they use
   optimizers for locking.

-  The phase relationship on transmission has been changed to a new default. It will be
   identical to the previous relationship for most cases, but will prevent power
   conservation issues in more complicated setups. You can set the
   ``_settings.phase_config.v2_transmission_phase`` to ``True`` if you want to revert
   to the old (Finesse 2) behavior, but the new behavior is likely more physically
   correct. See :ref:`beamsplitter_phase` for more details.


Added
=====

-  Add missing docs for many katscript :ref:`analyses` and :ref:`elements` (incl. new
   group Mechanical Elements), fix many broken links
-  Extra documentation on :ref:`phase_configurations`
-  New method: :meth:`finesse.model.Model.get_open_ports`
-  New class :class:`finesse.utilities.collections.OrderedSet`, used in multiple places
   where ordering of results/components is relevant
-  Distance-based filtering for visualizing subgraphs of the model graph, see :re:`model_visualization`

Changed
=======


-  :meth:`finesse.model.Model.get_elements_of_type` now returns a tuple instead of a
   generator, and accepts element names as strings as well as python classes as
   arguments:

-  Added an option ``full_output`` to :func:`finesse.gaussian.optimise_HG00_q_scipy` to
   return the optimized array of HG modes alongside the fit result. This replaces the
   previous ``return_fit_result`` argument.

-  Include parity flip on reflection in Mirror and Beamsplitter ABCD methods. See also
   the new ``_s`` and ``_t`` suffixes in methods in :mod:`finesse.tracing.abcd` and the
   :issue:`123`. For backward compatible code, use something like:

.. code:: ipython3

   try:
      from finesse.tracing.abcd import space, beamsplitter_refl

      beamsplitter_refl_t = lambda *args: beamsplitter_refl(*args, "x")
      beamsplitter_refl_s = lambda *args: beamsplitter_refl(*args, "y")
   except ImportError:
      # Handle newer versions which separate the beamsplitter refl # into the tangential
      and sagittal planes from 3.0a28 from finesse.tracing.abcd import (
         space, beamsplitter_refl_s, beamsplitter_refl_t,
      )

-  Changes the examples in the documentation to indicate that parsing an action in
   KatScript and calling ``model.run()`` without any arguments is not recommended.

Removed
=======

-  The ``'sagittal'`` and ``'tangential'`` synonyms for ``'y'`` and ``'x'`` for the
   :kat:command:`modes` command have been removed, since they can cause confusion with
   the new ``plane`` option for :class:`finesse.components.beamsplitter.Beamsplitter`
   and :class:`finesse.components.mirror.Mirror`

Fixed
=====

-  Single solution outputs can be seleceted by their name now, so you do not need to add
   extra actions or put them in series unnecessarily.
-  Clarified the docstrings for the :class:`finesse.components.cavity.Cavity` class its
   :meth:`finesse.components.cavity.Cavity.path` method.
-  The shape of DCFieldsSolution is reverted to ``[nodes, frequencies, HOMs]``, as
   described in :class:`finesse.analysis.actions.dc.DCFieldsSolutions`
-  When removing a :ref:`readouts` component, remove the associated output detectors as
   well (note that removing components from a model is unreliable in general)
-  Parameters of autogenerated spaces and wires not generating a correct ``full_name``
   attribute.
-  Fixed issue :issue:`659` - missing ``sol = model.run()`` in documentation for Maximise
   action

*****************************************************
 `3.0a27 <https://finesse.ifosim.org/docs/3.0a27/>`_
*****************************************************

-  Allow detectors and ports to be visualized with component_tree method. See an example
   in the
   [docs](https://finesse.ifosim.org/docs/develop/usage/python_api/models_and_components.html#visualizing-the-model)

-  Fix `finesse.gaussian.HGMode` ignoring shape of the given y vector when n=m.

-  Option to keep only a subset of symbols in symbolic `Model.ABCD` method

-  Add options to specify the plane of incidence for a beamsplitter and to misalign a
   beamsplitter

-  Add pytest-xdist and configure it for faster (parallel) test running

-  Fix slow optimal q detector test slowdown

-  Fix broken cli test overwriting user config

*****************************************************
 `3.0a26 <https://finesse.ifosim.org/docs/3.0a26/>`_
*****************************************************

-  Fixed inadvertently adding cython as a runtime dependency in 3.0a25
-  Added documentation on defining manual beam parameters
-  Expanded docstring on mirror curvature
-  Better error message for degree of freedom illegal self referencing
-  Generate conda files automatically from pyproject.toml

*****************************************************
 `3.0a24 <https://finesse.ifosim.org/docs/3.0a24/>`_
*****************************************************

New features
============

-  Add FrequencyResponse4 action:
   https://gitlab.com/ifosim/finesse/finesse3/-/merge_requests/202
-  add plot_field method to EigenmodesSolution:
   https://gitlab.com/ifosim/finesse/finesse3/-/merge_requests/220

Documentation changes
=====================

-  Documentation on degree of freedom command/component:
   https://gitlab.com/ifosim/finesse/finesse3/-/merge_requests/224
-  new example: inference on RoC to examples:
   https://gitlab.com/ifosim/finesse/finesse3/-/merge_requests/222
-  Adding a link to the finesse-ligo documentation:
   https://gitlab.com/ifosim/finesse/finesse3/-/merge_requests/218

Other
=====

-  Fix/benchmark creation tests:
   https://gitlab.com/ifosim/finesse/finesse3/-/merge_requests/223
-  Fix/641 ignore hidden folders during pyx files compilation checks:
   https://gitlab.com/ifosim/finesse/finesse3/-/merge_requests/221

*****************************************************
 `3.0a23 <https://finesse.ifosim.org/docs/3.0a23/>`_
*****************************************************

-  Fix memory leak issue during model building
-  Changing the 'disabled' argument of the Lock component to 'enabled' to avoid double
   negative if conditions in the code
-  Minor performance fixes
-  Fix for the Optimizer action that would sometimes leave the model in an incorrect
   state after optimization
-  "Did you mean" suggestions for katscript keyword arguments on syntax errors
-  Adds warning for unreasonable katscript line lengths and better message on parsing
   recursion errors
-  Evaluate symbolic references in the component info tables
-  allows overlap_contour to work with (qx,qy) input

*****************************************************
 `3.0a22 <https://finesse.ifosim.org/docs/3.0a22/>`_
*****************************************************

-  phase_config now locked when the model is built
-  Symbol.lambdify was added to change Finesse symbolic expressions into a Python
   callable function
-  Added initial benchmarking tests for tracking performance changes over time
-  KnmMatrix.plot can be set to amplitude or phase now with the mode option
-  Locks now throw an explicit exception LostLock when it fails
-  Added Matplotlib helper function that plots arrows along a line at several points

*****************************************************
 `3.0a21 <https://finesse.ifosim.org/docs/3.0a21/>`_
*****************************************************

Adds support for Python 3.12

*****************************************************
 `3.0a20 <https://finesse.ifosim.org/docs/3.0a20/>`_
*****************************************************

-  Python 3.8 support dropped:
   https://gitlab.com/ifosim/finesse/finesse3/-/merge_requests/172

-  Matplotlib 3.8 now works:

-  FrequencyResponse action fixed when using two element frequency vector:
   https://gitlab.com/ifosim/finesse/finesse3/-/merge_requests/169

-  Now compiles with Cython 3, provides better debugging. Performance seems similar but
   not yet confirmed.

-  Can trace beams in reverse for propagating through isolating components:
   https://gitlab.com/ifosim/finesse/finesse3/-/merge_requests/181

-  Wavefront curvature added to the beam propagation data:
   https://gitlab.com/ifosim/finesse/finesse3/-/merge_requests/171

-  KatScript will now take the Python class name as an option for elements and actions:
   https://gitlab.com/ifosim/finesse/finesse3/-/merge_requests/160

-  EigenmodeSolution for a cavity now has method to compute roundtrip loss:
   https://gitlab.com/ifosim/finesse/finesse3/-/commit/db847bff9bf5ef4ffb109c5e234def6860f62525

-  Map now has a `remove_piston` term method:
   https://gitlab.com/ifosim/finesse/finesse3/-/commit/ef83443addbfa4c99d4b662c6f8058a1740775fe

-  New `DCFields` action to return a solution containing the DC optical fields at every
   node and frequency:
   https://gitlab.com/ifosim/finesse/finesse3/-/commit/b2cf34acae38d53a6dbf51906875f89e4589fee0

*****************************************************
 `3.0a19 <https://finesse.ifosim.org/docs/3.0a19/>`_
*****************************************************

-  Requiring Matploblib < 3.8 until fixes are made for plotting routines
-  Parameters that are external controlled, such as those set by a DegreeOfFreedom will
   explicitly shown the symbolic reference now as opposed to hiding it. See #571

*****************************************************
 `3.0a18 <https://finesse.ifosim.org/docs/3.0a18/>`_
*****************************************************

-  Fixed FieldDetector not conjugating lower sideband

-  Fixed DegreeOfFreedom using custom AC_IN and AC_OUT not filling the matrix correctly

-  Variable element removed, now calls model.add_parameter instead. this means some code
   using `var.value.value` will no longer work.

-  Added extra factorisation step when refactor returns a singular matrix with KLU, a
   warning will show when this happens.

-  Model.display_signal_blockdiagram now takes nodes name list and only show paths with
   those nodes in for cleaner diagrams

-  Model.path can take a symbolic=True keyword argument now for calculating symbolic
   path lengths

-  phase_level deprecated and replaced with model.phase_config method

-  unparing unsupported KatScript values will result in a __FIX_ME__ token

-  Parameters now support boolean checks

-  Python 3.11 wheels now built

-  SetLockGains now just optimises gains and not demodulation phases

-  OptimiseRFReadoutDemodPhaseDC now accepts Readout detector outputs `REFL9_I` or
   `REFL9_Q` for example, to optimise for either quadrature. Readout names supported and
   will default to `_I` with a warning

-  Fixed Hello-Vinet function `substrate_thermal_expansion_depth` #567

*****************************************************
 `3.0a17 <https://finesse.ifosim.org/docs/3.0a17/>`_
*****************************************************

-  Fixing block diagram generation for signal paths

-  DOF has simpler interface for specifying just a DC actuation instead of using
   LocalDegreesOfFreedom

-  This also allows user to specify their own AC connections to the DOF.AC.i and
   DOF.AC.o as they see fit

-  Reworking signal node and port connections and attached_to attributes so they work

-  Wires now connect anything to anything, had some logic about input and output that
   isn't needed anymore. Wires also have a gain now for simply rescaling inputs before
   summing with multiple other signal nodes

*****************************************************
 `3.0a15 <https://finesse.ifosim.org/docs/3.0a15/>`_
*****************************************************

Adding additional features for degrees of freedom to allow for better/easier modelling
of ASC and other more complex effects. LocalDegreesOfFreedom replaces DOFDefinition,
which now has separate AC input and output nodes. Also tested against Sidles-Sigg theory
and no internal code changes were needed.

*****************************************************
 `3.0a14 <https://finesse.ifosim.org/docs/3.0a14/>`_
*****************************************************

Same as a13 but redoing conda dist for source

*****************************************************
 `3.0a12 <https://finesse.ifosim.org/docs/3.0a12/>`_
*****************************************************

Pinning to less than Cython 3

*****************************************************
 `3.0a11 <https://finesse.ifosim.org/docs/3.0a11/>`_
*****************************************************

Packaging/CI for windows still problematic, switching to conda instead of mamba due to
404 package errors

*****************************************************
 `3.0a10 <https://finesse.ifosim.org/docs/3.0a10/>`_
*****************************************************

Attempt at fixing bad windows tag processing

***************************************************
 `3.0a9 <https://finesse.ifosim.org/docs/3.0a9/>`_
***************************************************

New alpha update

***************************************************
 `3.0a8 <https://finesse.ifosim.org/docs/3.0a8/>`_
***************************************************

Bad pypi source pushed for a7

***************************************************
 `3.0a7 <https://finesse.ifosim.org/docs/3.0a7/>`_
***************************************************

Some recent fixes that improves memory allocation errors/checking and some usability
errors.

***************************************************
 `3.0a6 <https://finesse.ifosim.org/docs/3.0a6/>`_
***************************************************

Alpha 6 release

***************************************************
 `3.0a5 <https://finesse.ifosim.org/docs/3.0a5/>`_
***************************************************

alpha 5, testing pypi deploy pipeline

***************************************************
 `3.0a4 <https://finesse.ifosim.org/docs/3.0a4/>`_
***************************************************

alpha 4

***************************************************
 `3.0a3 <https://finesse.ifosim.org/docs/3.0a3/>`_
***************************************************

Primarily fixes for Windows
