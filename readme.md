# Sample Azure Function for XML Manipulation

## Disclaimer

> Please be aware that this code is provided as a prototype and is intended for demonstration purposes only. It has not been thoroughly tested and may not be reliable or secure. 
> 
> The author(s) of this code disclaim all warranties, either express or implied, including but not limited to any implied warranties of merchantability and fitness for a particular purpose. In no event shall the author(s) be liable for any damages whatsoever including direct, indirect, incidental, consequential, loss of business profits or special damages.
> 
> Use this code at your own risk.

## Important Note
In this repository, we convert a nested XML into an array of objects.
For example, if the input is
```xml
<A>
    <B>unique info</B>
    <C>
        <CA>list item C1</CA>
        <CA>list item C2</CA>
    </C>
    <D>
        <DA>list item D1</DA>
        <DA>list item D2</DA>
    </D>
</A>
```
The output will be 
```json
[
    {"B":"unique info","CA":"list item C1","DA":"list item D1"},
    {"B":"unique info","CA":"list item C1","DA":"list item D2"},
    {"B":"unique info","CA":"list item C2","DA":"list item D1"},
    {"B":"unique info","CA":"list item C2","DA":"list item D2"},
]
```
which is not useful in most scenarios. In fact, I believe flattening an XML based on the above, sets you back because you now lose the structure and hierarchy and end up with a lot of duplicate data. I strongly recommend you think again and restructure your purpose to avoid doing so.

I can't think of any scenarios in which a consumer of this data would work with this data without applying any transformations.

## Getting Started locally
### Pre-reqs
- Azure Function Core Tools v4
- Python 3.10 or 3.11
- `git`
- VS Code (optional)

### Steps
- Clone the repository in your computer.
- With your terminal, cd to this folder `cd sample-azurefn-xml`
- Run `python3.10 -m venv .venv`
- Make a copy of `sample.settings.json` and rename it to `local.settings.json`
- Open `local.settings.json` and update the values for `XML_SERVER_API_KEY` and `XML_SERVER_URL`.
- Activate your python env and install dependencies. 
    - On windows: `./.venv/Scripts/activate`
    - On Mac/Linux: `./.venv/bin/activate`
    - Then `pip install -r requirements.txt`
- Use VS Code debugger to start the app or run `func host start`.
    > VS Code provides a true debugger, whereas `func host start` only runs the app. 

