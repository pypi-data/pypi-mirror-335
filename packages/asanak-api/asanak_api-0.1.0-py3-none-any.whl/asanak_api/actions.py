class Actions:
    SENDSMS = {
        "name": "sendsms",
        "success_state_field": "status",
        "execption_state_field": "status",
    }
    TEMPLATE = {
        "name": "template",
        "success_state_field": "status",
        "execption_state_field": "status",
    }
    P2P = {
        "name": "p2psendsms",
        "success_state_field": "status",
        "execption_state_field": "status",
    }

    STATUS = {
        "name": "msgstatus",
        "success_state_field": "code",
        "execption_state_field": "status",
    }
    TEMPLATELIST = {
        "name": "templatelist",
        "success_state_field": "status",
        "execption_state_field": "code",
    }

    GETCREDEIT = {
        "name": "getcredit",
        "success_state_field": "status",
        "execption_state_field": "status",
    }

    GETRIALCREDIT = {
        "name": "getrialcredit",
        "success_state_field": "status",
        "execption_state_field": "status",
    }
