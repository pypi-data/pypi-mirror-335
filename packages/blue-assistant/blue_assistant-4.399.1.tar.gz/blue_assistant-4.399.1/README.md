# 🧠 blue-assistant

🧠 `@assistant` runs [AI](https://github.com/kamangir/openai-commands) [DAG](https://networkx.org/)s that combine deterministic and AI operations.

```bash
pip install blue-assistant
```

```mermaid
graph LR
    assistant_script_list["@assistant<br>script<br>list"]
    assistant_script_run["@assistant<br>script<br>run -<br>script=&lt;name&gt;,version=&lt;version&gt;<br>&lt;object-name&gt;"]

    web_crawl["@web<br>crawl -<br>&lt;url-1&gt;+&lt;url-2&gt;<br>&lt;object-name&gt;"]

    web_fetch["@web<br>fetch -<br>&lt;url&gt;<br>&lt;object-name&gt;"]

    script["📜 script"]:::folder
    url["🔗 url"]:::folder
    url2["🔗 url"]:::folder
    url3["🔗 url"]:::folder
    object["📂 object"]:::folder


    script --> assistant_script_list

    script --> assistant_script_run
    object --> assistant_script_run
    assistant_script_run --> object

    url --> web_crawl
    url2 --> web_crawl
    web_crawl --> url3
    web_crawl --> object

    url --> web_fetch
    web_fetch --> object

    bridge_ip["🔗 bridge_ip"]:::folder
    hue_username["🔗 hue_username"]:::folder
    list_of_lights["💡 light IDs"]:::folder

    hue_create_user["@hue<br>create_user"]
    hue_list["@hue<br>list"]
    hue_set["@hue<br>set"]
    hue_test["@hue<br>test"]

    bridge_ip --> hue_create_user
    hue_create_user --> hue_username

    bridge_ip --> hue_list
    hue_username --> hue_list
    hue_list --> list_of_lights

    bridge_ip --> hue_set
    hue_username --> hue_set
    list_of_lights --> hue_set

    bridge_ip --> hue_test
    hue_username --> hue_test
    list_of_lights --> hue_test



    classDef folder fill:#999,stroke:#333,stroke-width:2px;
```

|   |   |   |
| --- | --- | --- |
| [`orbital-data-explorer`](./blue_assistant/script/repository/orbital_data_explorer) [![image](https://github.com/kamangir/assets/raw/main/blue-assistant/PDS/uahirise-ESP_086795_1970.png?raw=true)](./blue_assistant/script/repository/orbital_data_explorer) Poking around [Orbital Data Explorer](https://ode.rsl.wustl.edu/) with an [AI DAG](./blue_assistant/script/repository/orbital_data_explorer/metadata.yaml). ⏸️ | [`@hue`](./blue_assistant/script/repository/hue) [![image](https://github.com/kamangir/assets/raw/main/blue-assistant/20250314_143702-2.png?raw=true)](./blue_assistant/script/repository/hue) "[Hey AI](./blue_assistant/script/repository/hue/metadata.yaml), help me write code to send color commands to the [Hue LED lights](https://www.philips-hue.com/en-ca) in my apartment." | [`blue-amo`](./blue_assistant/script/repository/blue_amo/README.md) [![image](https://github.com/kamangir/assets/blob/main/test_blue_assistant_script_run-2025-03-15-06pbpf/generating_frame_007.png?raw=true)](./blue_assistant/script/repository/blue_amo/README.md) Story development and visualization, with an [AI DAG](./blue_assistant/script/repository/blue_amo/metadata.yaml). |
| [`🌀 blue script`](./blue_assistant/script/) [![image](https://github.com/kamangir/assets/raw/main/blue-plugin/marquee.png?raw=true)](./blue_assistant/script/) A minimal AI DAG interface. | [``@RAG``](./blue_assistant/RAG/) [![image](https://github.com/kamangir/assets/raw/main/orbital-data-explorer-2025-03-16-xoo5vc/thumbnail-workflow.png?raw=true)](./blue_assistant/RAG/)  RAG on a DAG. 🔥 | [``@web``](./blue_assistant/web/) [![image](https://github.com/kamangir/assets/raw/main/blue-plugin/marquee.png?raw=true)](./blue_assistant/web/) A minimal web interface for an AI agent. |

---


[![pylint](https://github.com/kamangir/blue-assistant/actions/workflows/pylint.yml/badge.svg)](https://github.com/kamangir/blue-assistant/actions/workflows/pylint.yml) [![pytest](https://github.com/kamangir/blue-assistant/actions/workflows/pytest.yml/badge.svg)](https://github.com/kamangir/blue-assistant/actions/workflows/pytest.yml) [![bashtest](https://github.com/kamangir/blue-assistant/actions/workflows/bashtest.yml/badge.svg)](https://github.com/kamangir/blue-assistant/actions/workflows/bashtest.yml) [![PyPI version](https://img.shields.io/pypi/v/blue-assistant.svg)](https://pypi.org/project/blue-assistant/) [![PyPI - Downloads](https://img.shields.io/pypi/dd/blue-assistant)](https://pypistats.org/packages/blue-assistant)

built by 🌀 [`blue_options-4.240.1`](https://github.com/kamangir/awesome-bash-cli), based on 🧠 [`blue_assistant-4.399.1`](https://github.com/kamangir/blue-assistant).
