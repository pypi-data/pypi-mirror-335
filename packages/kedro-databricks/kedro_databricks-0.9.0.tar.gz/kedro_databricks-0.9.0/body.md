## 0.9.0 (2025-03-20)

### Feat

- **runtime_params**: add ability to define kedro runtime parameters in the task definitions

### Fix

- rename params and conf-source  according to kedro
- add support for custom task libraries
- add support for job parameters
- add support for health rule overrides

### Refactor

- achieve the same with way less code
- **bundle**: expect user to pass runtime params in the right format
- **bundle**: expect user to pass runtime params in the right format
- **bundle**: move runtime parameters formating in the __init__ method
- **bundle**: remove space before join
- **bundle**: remove duplicated depends_on
- move utils only used for bundling to separate module
- move examples path resolution to where it's used
- move remove_nulls to separate module
- use help from kedro where possible

[main 8649b85] bump: version 0.8.1 → 0.9.0
 2 files changed, 27 insertions(+), 1 deletion(-)

