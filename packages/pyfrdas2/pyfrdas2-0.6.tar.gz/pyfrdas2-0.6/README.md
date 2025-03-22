This python library help generate the **TéléTD files** for the french fiscal administration, which include **DAS2**, also called *Déclaration d'honoraires*. It is used by the OCA module l10n\_fr\_das2 from [OCA/l10n-france](https://github.com/OCA/l10n-france).

The French fiscal administration updates the encryption keys for DAS2 files every year. The encryption keys are updated in this module, which avoids updating the OCA module l10n\_fr\_das2 for every Odoo version. The specifications of the DAS2 file and the encryption keys are available on [www.impots.gouv.fr/tiers-declarants-0](https://www.impots.gouv.fr/tiers-declarants-0).

## Licence

This library is published under the [GNU Lesser General Public License v2.1](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html) or, at your option, any later version.

## Contributors

* Alexis de Lattre <alexis.delattre@akretion.com>

## Changelog

* version 0.6 dated 2025-03-21: threshold for year 2024+ updated from 1200 € to 2400 € ([source](https://bofip.impots.gouv.fr/bofip/14327-PGP.html/ACTU-2024-00154))
* version 0.5 dated 2024-12-14: modernize packaging and version management
* version 0.4 dated 2024-06-06: new release to fix bad build
* version 0.3 dated 2024-06-06: add method **get\_partner\_declaration\_threshold()**
* version 0.2 dated 2024-03-12: declare pyfrdas2 as compatible with python 3.6+
* version 0.1 dated 2024-03-11: initial release
