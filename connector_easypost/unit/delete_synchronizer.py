# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.synchronizer import Deleter
from ..connector import get_environment


class EasypostDeleter(Deleter):
    """ Base deleter for Easypost """

    def run(self, easypost_id):
        """
        Run the synchronization, delete the record on Easypost
        :param easypost_id: identifier of the record to delete
        """
        raise NotImplementedError('Cannot delete records from EasyPost.')


@job(default_channel='root.easypost')
def export_delete_record(session, model_name, backend_id, easypost_id):
    """ Delete a record on Easypost """
    env = get_environment(session, model_name, backend_id)
    deleter = env.get_connector_unit(EasypostDeleter)
    return deleter.run(easypost_id)
