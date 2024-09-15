
from flows.named_entity_recognition import WorkflowNamedEntityRecognition
from flows.relational_extraction import WorkflowRelationalExtraction
from utils.logging import get_logger

LOG = get_logger(__name__)


def main():
    """
    Entrypoint to start any flows. Implemented with a fascade pattern to hide in abstracted layer the logic.

    # TODO: implement solution to execute specific flows.
    """

    ner_flow = WorkflowNamedEntityRecognition()
    ner_flow.run_process()

    re_flow = WorkflowRelationalExtraction()
    re_flow.run_process()


if __name__ == '__main__':
    main()
