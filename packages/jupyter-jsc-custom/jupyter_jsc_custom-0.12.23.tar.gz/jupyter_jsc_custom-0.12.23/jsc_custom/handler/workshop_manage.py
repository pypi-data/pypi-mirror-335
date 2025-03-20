import random
import string

from jupyterhub.handlers import BaseHandler
from jupyterhub.handlers import default_handlers
from jupyterhub.handlers.pages import SpawnHandler
from jupyterhub.utils import url_path_join
from tornado import web

from ..misc import get_custom_config
from ..orm.workshops import WorkshopShares


def isInstructor(groups=[]):
    instructorGroup = (
        get_custom_config()
        .get("workshop", {})
        .get(
            "instructorGroup",
            "geant:dfn.de:fz-juelich.de:jsc:jupyter:workshop_instructors",
        )
    )
    if instructorGroup in groups:
        return True
    else:
        return False


class WorkshopManageHandler(BaseHandler):
    @web.authenticated
    async def get(self):
        user = self.current_user
        if not user:
            raise web.HTTPError(403)
        auth_state = await user.get_auth_state()
        db_entries = WorkshopShares.find_by_user_id(self.db, user.id)
        db_workshops = {}
        for db_entry in db_entries:
            db_workshops[db_entry.workshop_id] = db_entry.to_dict()

        form = await self.render_template(
            "workshop_manager.html",
            user=user,
            auth_state=auth_state,
            db_workshops=db_workshops,
            is_instructor=isInstructor(auth_state.get("groups", [])),
        )
        self.finish(form)


class WorkshopHandler(SpawnHandler):
    def generate_random_id(self):
        chars = string.ascii_lowercase
        all_chars = string.ascii_lowercase + string.digits

        # Start with a random lowercase letter
        result = random.choice(chars)

        # Add 31 more characters from lowercase letters and numbers
        result += "".join(random.choice(all_chars) for _ in range(31))

        return result

    async def _render_form(self, for_user, spawner, workshop_options):
        url = url_path_join(self.base_url, "user", for_user.escaped_name, spawner.name)
        auth_state = await for_user.get_auth_state()
        return await self.render_template(
            "workshop.html",
            for_user=for_user,
            auth_state=auth_state,
            spawner=spawner,
            url=url,
            workshop_options=workshop_options,
        )

    def get_spawner(self, user, workshop):
        # Each workshop should only get one Spawner Object.
        # Loop through all spawners and see if a Spawner for this
        # workshop already exists.
        server_name = None
        for key, orm_spawner in user.orm_user.orm_spawners.items():
            if (
                orm_spawner.user_options
                and orm_spawner.user_options.get("workshop_id", "")
                == workshop.workshop_id
            ):
                server_name = key
                break

        if not server_name:
            server_name = self.generate_random_id()

        spawner = user.get_spawner(server_name, replace_failed=True)
        if not spawner.user_options.get("workshop_id", False):
            spawner.user_options["workshop_id"] = workshop.workshop_id
            if not spawner.orm_spawner.user_options:
                spawner.orm_spawner.user_options = {}
            spawner.orm_spawner.user_options["workshop_id"] = workshop.workshop_id
        self.db.add(spawner.orm_spawner)
        self.db.commit()

        return spawner

    @web.authenticated
    async def get(self, workshop_id):
        user = self.current_user
        if not user:
            raise web.HTTPError(403)
        workshop = WorkshopShares.find_by_workshop_id(self.db, workshop_id=workshop_id)
        if not workshop:
            raise web.HTTPError(404)

        spawner = self.get_spawner(user, workshop)

        form = await self._render_form(
            user, spawner=spawner, workshop_options=workshop.user_options
        )
        self.finish(form)


default_handlers.append((r"/workshopmanager", WorkshopManageHandler))
default_handlers.append((r"/workshops/([^/]+)", WorkshopHandler))
