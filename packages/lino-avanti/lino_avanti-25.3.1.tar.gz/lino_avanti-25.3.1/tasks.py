from atelier.invlib import setup_from_tasks

ns = setup_from_tasks(globals(),
                      "lino_avanti",
                      languages="en de fr".split(),
                      make_docs_command='./make_docs.sh',
                      tolerate_sphinx_warnings=False,
                      locale_dir='lino_avanti/lib/avanti/locale',
                      revision_control_system='git')
