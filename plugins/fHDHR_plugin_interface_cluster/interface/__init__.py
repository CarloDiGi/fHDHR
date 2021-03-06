from collections import OrderedDict


class Plugin_OBJ():

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils

        self.friendlyname = self.fhdhr.config.dict["cluster"]["friendlyname"] or "%s %s" % (self.fhdhr.config.dict["fhdhr"]["friendlyname"], self.fhdhr.origins.valid_origins[0])

        if self.plugin_utils.ssdp.multicast_address:
            self.startup_sync()

    def cluster(self):
        return self.plugin_utils.db.get_plugin_value("cluster", "dict") or self.default_cluster()

    def get_cluster_dicts_web(self):
        fhdhr_list = self.cluster()
        locations = []
        for location in list(fhdhr_list.keys()):
            item_dict = {
                        "base_url": fhdhr_list[location]["base_url"],
                        "name": fhdhr_list[location]["name"]
                        }
            if item_dict["base_url"] != self.plugin_utils.api.base:
                locations.append(item_dict)
        if len(locations):
            locations = sorted(locations, key=lambda i: i['name'])
            return locations
        else:
            return None

    def get_list(self):
        cluster = self.plugin_utils.db.get_plugin_value("cluster", "dict") or self.default_cluster()
        return_dict = {}
        for location in list(cluster.keys()):
            if location != self.plugin_utils.api.base:
                return_dict[location] = {
                                        "Joined": True
                                        }

        detected_list = self.plugin_utils.ssdp.ssdp_handling[self.plugin_utils.namespace].detect_method.get()
        for location in detected_list:
            if location not in list(cluster.keys()):
                return_dict[location] = {
                                        "Joined": False
                                        }
        return_dict = OrderedDict(sorted(return_dict.items()))
        return return_dict

    def default_cluster(self):
        defdict = {}
        defdict[self.plugin_utils.api.base] = {
                                "base_url": self.plugin_utils.api.base,
                                "name": self.friendlyname
                                }
        return defdict

    def startup_sync(self):
        self.plugin_utils.logger.info("Syncronizing with Cluster.")
        cluster = self.plugin_utils.db.get_plugin_value("cluster", "dict") or self.default_cluster()
        if not len(list(cluster.keys())):
            self.plugin_utils.logger.info("No Cluster Found.")
        else:
            self.plugin_utils.logger.info("Found %s clustered services." % str(len(list(cluster.keys()))))
        for location in list(cluster.keys()):
            if location != self.plugin_utils.api.base:
                self.plugin_utils.logger.debug("Checking Cluster Syncronization information from %s." % location)
                sync_url = "%s/api/cluster?method=get" % location
                try:
                    sync_open = self.plugin_utils.web.session.get(sync_url)
                    retrieved_cluster = sync_open.json()
                    if self.plugin_utils.api.base not in list(retrieved_cluster.keys()):
                        return self.leave()
                except self.plugin_utils.web.exceptions.ConnectionError:
                    self.plugin_utils.logger.error("Unreachable: %s" % location)

    def leave(self):
        self.plugin_utils.logger.info("Leaving cluster.")
        self.plugin_utils.db.set_plugin_value("cluster", "dict", self.default_cluster())

    def disconnect(self):
        cluster = self.plugin_utils.db.get_plugin_value("cluster", "dict") or self.default_cluster()
        for location in list(cluster.keys()):
            if location != self.plugin_utils.api.base:
                self.plugin_utils.logger.info("Informing %s that I am departing the Cluster." % location)
                sync_url = "%s/api/cluster?method=del&location=%s" % (location, self.plugin_utils.api.base)
                try:
                    self.plugin_utils.web.session.get(sync_url)
                except self.plugin_utils.web.exceptions.ConnectionError:
                    self.plugin_utils.logger.error("Unreachable: %s" % location)
        self.leave()

    def sync(self, location):
        sync_url = "%s/api/cluster?method=get" % location
        try:
            sync_open = self.plugin_utils.web.session.get(sync_url)
            self.plugin_utils.db.set_plugin_value("cluster", "dict", sync_open.json())
        except self.plugin_utils.web.exceptions.ConnectionError:
            self.plugin_utils.logger.error("Unreachable: %s" % location)

    def push_sync(self):
        cluster = self.plugin_utils.db.get_plugin_value("cluster", "dict") or self.default_cluster()
        for location in list(cluster.keys()):
            if location != self.plugin_utils.api.base:
                sync_url = "%s/api/cluster?method=sync&location=%s" % (location, self.plugin_utils.api.base_quoted)
                try:
                    self.plugin_utils.web.session.get(sync_url)
                except self.plugin_utils.web.exceptions.ConnectionError:
                    self.plugin_utils.logger.error("Unreachable: %s" % location)

    def add(self, location):
        cluster = self.plugin_utils.db.get_fhdhr_value("cluster", "dict") or self.default_cluster()
        if location not in list(cluster.keys()):
            self.plugin_utils.logger.info("Adding %s to cluster." % location)
            cluster[location] = {"base_url": location}

            location_info_url = "%s/api/cluster?method=ident" % location
            try:
                location_info_req = self.plugin_utils.web.session.get(location_info_url)
            except self.plugin_utils.web.exceptions.ConnectionError:
                self.plugin_utils.logger.error("Unreachable: %s" % location)
                del cluster[location]
                self.plugin_utils.db.set_plugin_value("cluster", "dict", cluster)
                return
            location_info = location_info_req.json()
            cluster[location]["name"] = location_info["name"]

            cluster_info_url = "%s/api/cluster?method=get" % location
            try:
                cluster_info_req = self.plugin_utils.web.session.get(cluster_info_url)
            except self.plugin_utils.web.exceptions.ConnectionError:
                self.plugin_utils.logger.error("Unreachable: %s" % location)
                del cluster[location]
                self.plugin_utils.db.set_plugin_value("cluster", "dict", cluster)
                return
            cluster_info = cluster_info_req.json()
            for cluster_key in list(cluster_info.keys()):
                if cluster_key not in list(cluster.keys()):
                    cluster[cluster_key] = cluster_info[cluster_key]

            self.plugin_utils.db.set_plugin_value("cluster", "dict", cluster)
            self.push_sync()

    def remove(self, location):
        cluster = self.plugin_utils.db.get_plugin_value("cluster", "dict") or self.default_cluster()
        if location in list(cluster.keys()):
            self.plugin_utils.logger.info("Removing %s from cluster." % location)
            del cluster[location]
            sync_url = "%s/api/cluster?method=leave" % location
            try:
                self.plugin_utils.web.session.get(sync_url)
            except self.plugin_utils.web.exceptions.ConnectionError:
                self.plugin_utils.logger.error("Unreachable: %s" % location)
            self.push_sync()
            self.plugin_utils.db.set_plugin_value("cluster", "dict", cluster)
