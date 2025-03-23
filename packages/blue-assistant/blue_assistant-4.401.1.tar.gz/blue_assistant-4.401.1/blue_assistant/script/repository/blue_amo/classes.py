import copy

from blueness import module
from blue_objects import file, path

from blue_assistant import NAME
from blue_assistant.script.repository.base.classes import BaseScript
from blue_assistant.script.repository.blue_amo.actions import dict_of_actions
from blue_assistant.logger import logger

NAME = module.name(__file__, NAME)


class BlueAmoScript(BaseScript):
    name = path.name(file.path(__file__))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.dict_of_actions.update(dict_of_actions)

    def generate_graph(
        self,
        log: bool = True,
        verbose: bool = False,
        save_graph: bool = True,
    ) -> bool:
        if not super().generate_graph(
            log=log,
            verbose=verbose,
            save_graph=save_graph,
        ):
            return False

        map_node_name = "generating_the_frames"
        if log:
            logger.info(
                "{}: expanding {} X {}...".format(
                    NAME,
                    map_node_name,
                    self.vars["frame_count"],
                )
            )

        map_node = self.nodes[map_node_name]
        del self.nodes[map_node_name]
        self.G.remove_node(map_node_name)

        reduce_node_name = "stitching_the_frames"
        for index in range(self.vars["frame_count"]):
            node_name = f"generating_frame_{index+1:03d}"

            self.nodes[node_name] = copy.deepcopy(map_node)

            self.G.add_node(node_name)
            self.G.add_edge(
                node_name,
                "setting_frame_prompts",
            )
            self.G.add_edge(
                reduce_node_name,
                node_name,
            )

        return self.save_graph(log=log) if save_graph else True
