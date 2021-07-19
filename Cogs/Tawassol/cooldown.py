from datetime import datetime

class Cooldown:
    users_cld = {}

    @classmethod
    def check_user(cls, cmd: str, author_id: int, cooldown: int) -> tuple:
        now = datetime.now()

        user_cld = cls.users_cld.get(author_id)
        if user_cld is None:
            cls.users_cld[author_id] = {}
            return True, now

        user_cld = user_cld.get(cmd)
        if user_cld is None:
            cls.users_cld[author_id][cmd] = now
            return True, now

        last_move = now - user_cld
        if last_move.seconds > cooldown:
            cls.users_cld[author_id][cmd] = now
            return True, now
        else:
            return False, cooldown - last_move.seconds
