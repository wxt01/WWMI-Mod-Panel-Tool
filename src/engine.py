# -*- coding: utf-8 -*-
"""WWMI MOD 面板助手 - 核心引擎（注入式）
解析 Mod 按键配置 -> 注入样式1面板段到 mod.ini + 生成资源 -> 回滚 / 调整 / 改字

核心知识（来自大量实战）：
- 面板段必须注入 mod 自身 ini（独立 ini 变量命名空间隔离，赋值无效）
- 按钮段由 Draw 无条件直接 run（被 if 分支包裹 run 后点击检测退化）
- 调出键：A-Z/0-9 单字符 100% 支持，其他需 VK 名；自动避开 mod 已用键
- 一个 [KeyXXX] 段（一个变量）= 一个按钮
- 样式1（单页全按钮）为唯一验收方案；样式2（分页）已放弃
"""

import io
import math
import os
import re
import shutil
import time

SKIP_SECTIONS = {
    "KEYTOGGLEUI", "KEYMOUSELEFT", "KEYMOUSEDRAG", "KEYMOUSE", "KEYHELP",
    "KEYRESETPOSITION", "KEYMENU", "KEYCLICKEDSLOT", "KEYHOLD", "KEYHOLDSHAPE",
    "KEYRESET", "KEYMOUSEHOVER", "KEYUI", "KEYPANEL", "KEYTOGGLE",
    "KEYTOGGLEZZUI", "KEYMOUSEZZ",
}

PANEL_MARK = "; ===== WWMI MOD Panel"
PANEL_RES = "zz_panel_res"
LABELS_FILE = "zz_panel_labels.json"
BAK_PREFIX = "mod.ini.bak_panel_"

# 验收版默认布局参数（y 方向绘制自动乘纵横比）
DEF_BW = 0.045
DEF_BH = 0.03
DEF_GAP = 0.004
DEF_PAD = 0.008
DEF_TITLE_H = 0.024
DEF_CLOSE_W = 0.024
DEF_FX = 0.12
DEF_FY = 0.12


def _cols_for(n):
    if n <= 8:
        return 4
    if n <= 16:
        return 6
    if n <= 24:
        return 8
    return 9


_BAK_PATTERNS = (".BAK", ".bak", "_BACKUP", "-BACKUP", "_BACKUP_", "BACKUP")


def _is_backup(path):
    upper = os.path.basename(path).upper()
    return any(p in upper for p in _BAK_PATTERNS)


def _find_inis(mod_dir):
    found = []
    for root, dirs, files in os.walk(mod_dir):
        for fn in files:
            if not fn.lower().endswith(".ini"):
                continue
            if fn.upper().startswith("DISABLED"):
                continue
            if _is_backup(fn):
                continue
            if fn == LABELS_FILE:
                continue
            if root.rstrip("/\\").endswith(PANEL_RES):
                continue
            found.append(os.path.join(root, fn))
    return found


def _parse_ini_sections(ini_path):
    """返回 [(name, key, type, var, values)]，仅 Key 段且含 >=2 值变量"""
    sections = []
    cur = None
    with open(ini_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith(";") or line.startswith("#"):
                continue
            m = re.match(r"^\[(.+)\]$", line)
            if m:
                cur = {"name": m.group(1).strip(), "key": None, "type": None,
                       "var": None, "values": None}
                sections.append(cur)
                continue
            if cur is None:
                continue
            km = re.match(r"^key\s*=\s*(.+)$", line, re.IGNORECASE)
            if km and cur["key"] is None:
                cur["key"] = km.group(1).strip()
                continue
            tm = re.match(r"^type\s*=\s*(\w+)$", line, re.IGNORECASE)
            if tm and cur["type"] is None:
                cur["type"] = tm.group(1).strip().lower()
                continue
            vm = re.match(r"^\$(\w+)\s*=\s*(.+)$", line)
            if vm and cur["var"] is None:
                vals = [v.strip() for v in vm.group(2).split(",") if v.strip()]
                if len(vals) >= 2:
                    cur["var"] = "$" + vm.group(1)
                    cur["values"] = vals
    return [s for s in sections if s["name"].upper().startswith("KEY")
            and s["var"] is not None]


def _ini_namespace(ini_path):
    """读取 ini 声明的 namespace（PANEL_MARK 之前的原始部分）。"""
    try:
        with open(ini_path, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
    except Exception:
        return ""
    base = txt.split(PANEL_MARK, 1)[0]
    m = re.search(r"(?m)^\s*namespace\s*=\s*(.+?)\s*$", base)
    return m.group(1).strip() if m else ""


def _vref(btn):
    """按钮变量的完整引用：变量所在 ini 有 namespace 时用 $\\ns\\var 全名。"""
    var = btn["var"]
    ns = (btn.get("ns") or "").strip()
    if ns:
        return "$\\" + ns + "\\" + var.lstrip("$")
    return var


def parse_mod_keys(mod_dir):
    """解析 mod 目录按键段。一个变量 = 一个按钮，按变量名去重。
    返回 (buttons, used_keys)。"""
    buttons = []
    seen_vars = set()
    used_keys = []
    for ini in _find_inis(mod_dir):
        for sec in _parse_ini_sections(ini):
            name = sec["name"]
            if name.upper() in SKIP_SECTIONS:
                continue
            if sec["var"] in seen_vars:
                continue
            seen_vars.add(sec["var"])
            label = name[3:] if name.upper().startswith("KEY") else name
            buttons.append({
                "name": name,
                "label": label,
                "key": sec["key"] or "",
                "type": sec["type"] or "cycle",
                "var": sec["var"],
                "values": sec["values"],
                "src": ini,
                "ns": _ini_namespace(ini),
            })
            if sec["key"]:
                used_keys.append(sec["key"].lower())
    return buttons, used_keys


# ---------------- 方案1 后缀翻译表 ----------------
LABEL_MAP = {
    "face": "脸", "hair": "头发", "eyes": "眼睛", "eye": "眼睛", "brow": "眉毛",
    "eyebrow": "眉毛", "lashes": "睫毛", "iris": "虹膜", "pupil": "瞳孔",
    "mouth": "嘴巴", "lip": "嘴唇", "lips": "嘴唇", "lipstick": "口红",
    "nose": "鼻子", "ear": "耳朵", "ears": "耳朵", "maoer": "猫耳",
    "horn": "角", "horns": "角", "antler": "鹿角", "tail": "尾巴",
    "wings": "翅膀", "wing": "翅膀", "halo": "光环", "crown": "皇冠",
    "hat": "帽子", "cap": "帽子", "hood": "兜帽", "mask": "面具",
    "glasses": "眼镜", "monocle": "单片镜", "veil": "面纱",
    "necklace": "项链", "choker": "项圈", "collar": "项圈", "pendant": "吊坠",
    "locket": "项链", "amulet": "护身符", "scarf": "围巾", "muffler": "围巾",
    "tie": "领带", "bowtie": "领结", "brooch": "胸针", "badge": "徽章",
    "dress": "裙子", "skirt": "裙摆", "shangyi": "上衣", "top": "上衣",
    "coat": "外套", "jacket": "外套", "cape": "披风", "cloak": "斗篷",
    "bra": "胸罩", "maid": "女仆", "apron": "围裙", "sleeves": "袖子",
    "sleeve": "袖子", "cuffs": "袖口", "cuff": "袖口", "frill": "荷叶边",
    "frills": "荷叶边", "lace": "蕾丝", "ribbon": "蝴蝶结", "bows": "蝴蝶结",
    "bow": "蝴蝶结", "pattern": "花纹", "trim": "花边", "hem": "下摆",
    "pantsu": "内裤", "panties": "内裤", "pants": "裤子", "trousers": "裤子",
    "shorts": "短裤", "bottom": "下装", "diaodai": "吊带", "strap": "肩带",
    "straps": "肩带", "jiandai": "肩带", "shoutao": "手套", "glove": "手套",
    "gloves": "手套", "armlet": "臂环", "bracelet": "手链", "ring": "戒指",
    "watch": "手表", "belt": "腰带", "buckle": "扣环", "chain": "链子",
    "chains": "链子", "zipper": "拉链", "siwa": "丝袜", "hose": "吊带袜",
    "stocking": "长袜", "stockings": "长袜", "sock": "袜子", "socks": "袜子",
    "shoes": "鞋", "shoes2": "鞋2", "boot": "靴子", "boots": "靴子",
    "heel": "高跟鞋", "heels": "高跟鞋", "slipper": "拖鞋", "sandal": "凉鞋",
    "anklet": "脚链", "paizi": "名牌", "genki": "元气", "fashi": "发饰",
    "wanju": "玩具", "shengh": "绳子", "yeti": "液体", "libom": "礼服",
    "apron2": "围裙2", "collar2": "项圈2",
    "skin": "皮肤", "body": "身体", "arm": "手臂", "leg": "腿", "legs": "腿",
    "thigh": "大腿", "thighs": "大腿", "waist": "腰", "hip": "臀",
    "chest": "胸部", "bosom": "胸部", "boob": "胸部", "breast": "胸部",
    "navel": "肚脐", "back": "背部", "shoulder": "肩", "shoulders": "肩",
    "hand": "手", "hands": "手", "foot": "脚", "feet": "脚", "nail": "指甲",
    "nails": "指甲", "tattoo": "纹身", "blush": "腮红", "freckle": "雀斑",
    "piercing": "穿孔", "jewel": "宝石", "gem": "宝石", "crystal": "水晶",
    "pearl": "珍珠", "star": "星星", "moon": "月亮", "sun": "太阳",
    "flower": "花", "flowers": "花", "rose": "玫瑰", "lily": "百合",
    "lotus": "莲花", "sakura": "樱花", "cherry": "樱花", "feather": "羽毛",
    "feathers": "羽毛", "bell": "铃铛", "bells": "铃铛", "tassel": "流苏",
    "tassels": "流苏", "fringe": "流苏", "pompom": "毛球", "pompon": "毛球",
    "plush": "玩偶", "doll": "玩偶", "teddy": "泰迪", "bunny": "兔子",
    "rabbit": "兔子", "cat": "猫", "dog": "狗", "bear": "熊", "panda": "熊猫",
    "fox": "狐狸", "wolf": "狼", "dragon": "龙", "phoenix": "凤凰",
    "butterfly": "蝴蝶", "dragonfly": "蜻蜓", "bird": "鸟", "owl": "猫头鹰",
    "crow": "乌鸦", "swan": "天鹅", "fish": "鱼", "koi": "锦鲤",
    "shell": "贝壳", "sea": "海", "wave": "波浪", "anchor": "船锚",
    "sword": "剑", "blade": "刀刃", "knife": "刀", "dagger": "匕首",
    "spear": "长矛", "lance": "长枪", "axe": "斧", "hammer": "锤",
    "scythe": "镰刀", "shield": "盾", "staff": "法杖", "wand": "魔杖",
    "orb": "宝珠", "longbow": "长弓", "arrow": "箭", "gun": "枪", "cannon": "炮",
    "umbrella": "伞", "parasol": "阳伞", "fan": "扇子", "book": "书",
    "scroll": "卷轴", "map": "地图", "compass": "指南针", "key": "钥匙",
    "lock": "锁", "phone": "手机", "camera": "相机", "letter": "信",
    "envelope": "信封", "gift": "礼物", "box": "盒子", "basket": "篮子",
    "bottle": "瓶子", "cup": "杯子", "teacup": "茶杯", "plate": "盘子",
    "fork": "叉子", "spoon": "勺子", "chopsticks": "筷子", "candy": "糖果",
    "cookie": "饼干", "cake": "蛋糕", "bread": "面包", "rice": "米饭",
    "noodle": "面条", "noodles": "面条", "milk": "牛奶", "tea": "茶",
    "coffee": "咖啡", "juice": "果汁", "wine": "酒", "sake": "清酒",
    "bamboo": "竹", "plum": "梅", "peach": "桃", "apple": "苹果",
    "grape": "葡萄", "melon": "瓜", "pumpkin": "南瓜", "corn": "玉米",
    "wheat": "麦穗", "leaf": "叶子", "leaves": "叶子", "vine": "藤蔓",
    "thorn": "荆棘", "thorns": "荆棘", "grass": "草", "mushroom": "蘑菇",
    "mushrooms": "蘑菇", "fire": "火焰", "flame": "火焰", "flames": "火焰",
    "ice": "冰", "snow": "雪", "snowflake": "雪花", "rain": "雨",
    "thunder": "雷电", "lightning": "闪电", "wind": "风", "cloud": "云",
    "clouds": "云", "star": "星星", "sparkle": "闪光", "glow": "光晕",
    "aura": "气场", "energy": "能量", "mana": "魔力", "magic": "魔法",
    "power": "力量", "buff": "增益", "debuff": "减益", "toggle": "切换",
    "on": "开", "off": "关", "show": "显示", "hide": "隐藏", "swap": "互换",
    "switch": "切换", "change": "更换", "set": "套装", "outfit": "服装",
    "costume": "服装", "clothes": "衣服", "clothing": "衣服", "uniform": "制服",
    "school": "校服", "suit": "西装", "bikini": "泳装", "swim": "泳装",
    "swimsuit": "泳装", "lingerie": "内衣", "underwear": "内衣",
    "pajama": "睡衣", "pajamas": "睡衣", "nightgown": "睡裙", "kimono": "和服",
    "yukata": "浴衣", "qipao": "旗袍", "cheongsam": "旗袍", "hanfu": "汉服",
    "armor": "铠甲", "armour": "铠甲", "helmet": "头盔", "visor": "面甲",
    "pauldron": "肩甲", "gauntlet": "护手", "greave": "护腿",
    # ---- 拼音词条（作者常用拼音命名，含大写开头自动转小写匹配）----
    "toufa": "头发", "yanjing": "眼睛", "meimao": "眉毛", "lian": "脸",
    "zui": "嘴", "bi": "鼻子", "er": "耳", "erduo": "耳朵", "tou": "头",
    "bozi": "脖子", "jian": "肩", "xiong": "胸", "xiongbu": "胸部", "yao": "腰",
    "tun": "臀", "tui": "腿", "shou": "手", "jiao": "脚", "zhi": "手指",
    "zhua": "爪", "pifu": "皮肤", "rou": "肉", "shenti": "身体",
    "yifu": "衣服", "xiayi": "下衣", "qunzi": "裙子", "kuzi": "裤子",
    "duanku": "短裤", "wazi": "袜子", "xiezi": "鞋子", "maozi": "帽子",
    "weijin": "围巾", "yaodai": "腰带", "xiongdai": "胸带", "jianbang": "肩带",
    "shouzhuo": "手镯", "erhuan": "耳环", "touhuan": "头环", "weiba": "尾巴",
    "chibang": "翅膀", "hudie": "蝴蝶结", "lingdai": "领带", "kouzi": "扣子",
    "lalian": "拉链", "shengzi": "绳子", "shenzi": "绳子", "huaban": "花瓣",
    "zhuzi": "珠子", "lingdang": "铃铛", "liusu": "流苏", "maoqiu": "毛球",
    "piaodai": "飘带", "xiazhuo": "下着", "shangzhuo": "上着", "neiyi": "内衣",
    "waiyi": "外衣", "moshi": "模式", "xingtai": "形态", "yanse": "颜色",
    "yangshi": "样式", "fengge": "风格", "kai": "开", "guan": "关",
    "huan": "换", "qie": "切", "qiehuan": "切换", "yincang": "隐藏",
    "xianshi": "显示", "suofang": "缩放", "dadou": "大", "xiaoxiao": "小",
    "chuan": "穿", "tuo": "脱", "shang": "上", "xia": "下", "zuo": "左",
    "you": "右", "qian": "前", "hou": "后", "nei": "内", "wai": "外",
    "gao": "高", "di": "低", "chang": "长", "duan": "短", "da": "大",
    "xiao": "小", "kuan": "宽", "zhai": "窄", "banshen": "半身", "quanshen": "全身",
    # ---- 英文补缺 ----
    "neck": "脖子", "neckline": "领口", "ankle": "脚踝",
    "knee": "膝盖", "elbow": "手肘", "wrist": "手腕", "forearm": "前臂",
    "calf": "小腿", "shin": "小腿", "torso": "躯干", "abdomen": "腹部",
    "belly": "肚子", "stomach": "肚子", "butt": "屁股", "crotch": "裆",
    "waistline": "腰线", "hemline": "下摆", "side": "侧面", "front": "正面",
    "back": "背面", "long": "长", "short": "短", "alt": "备用", "extra": "附加",
    "additional": "附加", "custom": "自定义", "default": "默认", "hidden": "隐藏",
    "visible": "可见", "flip": "翻转", "rotate": "旋转", "scale": "缩放",
    "colour": "颜色", "tint": "染色", "paint": "涂色", "shade": "阴影",
    "gloss": "光泽", "matte": "哑光", "metal": "金属", "gold": "金色",
    "silver": "银色", "bronze": "铜色", "black": "黑色", "white": "白色",
    "red": "红色", "blue": "蓝色", "green": "绿色", "purple": "紫色",
    "pink": "粉色", "yellow": "黄色", "orange": "橙色", "brown": "棕色",
    "grey": "灰色", "gray": "灰色", "dark": "深色", "light": "浅色",
    "variant": "变体", "version": "版本", "style": "款式", "layer": "层",
    "part": "部件", "parts": "部件", "piece": "件", "comp": "组件",
    "component": "组件", "accent": "点缀", "detail": "细节", "detail2": "细节2",
    "zhanshi": "展示", "tiaozheng": "调整", "xuangua": "悬挂", "baoshi": "宝石",
    "shuitie": "水贴", "tiehua": "贴花", "wen": "纹", "hua": "花",
    # ---- 奥古斯塔等作者常用拼音 / 通用按键功能词 ----
    "tunv": "臀部", "neiku": "内裤", "huwan": "护腕", "xiangquan": "项圈",
    "tuwei": "兔尾", "jiaohuan": "互换", "shangban": "上装", "xiaban": "下装",
    "pifeng": "披风", "suolian": "锁链", "bangdai": "绑带", "shenghen": "伤痕",
    "help": "帮助", "reset": "重置", "position": "位置", "info": "信息",
    "about": "关于", "quit": "退出", "menu": "菜单", "open": "打开", "close": "关闭",
    "next": "下一个", "previous": "上一个", "back": "返回", "forward": "前进",
    "confirm": "确认", "apply": "应用", "clear": "清除", "save": "保存", "load": "载入",
    "copy": "复制", "paste": "粘贴", "undo": "撤销", "redo": "重做", "zoom": "缩放",
    "cursor": "光标", "arrow": "箭头", "left": "左", "right": "右", "up": "上", "down": "下",
    "page": "页", "home": "主页", "end": "结尾", "insert": "插入", "delete": "删除",
    "space": "空格", "tab": "Tab", "enter": "回车", "escape": "退出",
    "shift": "Shift", "ctrl": "Ctrl", "control": "Ctrl", "alt": "Alt",
    "mouse": "鼠标", "click": "点击", "hold": "按住", "release": "释放",
    "drag": "拖动", "hover": "悬停", "move": "移动", "keyboard": "键盘",
    "volume": "音量", "brightness": "亮度", "sound": "声音", "audio": "音频",
    "music": "音乐", "play": "播放", "stop": "停止", "record": "录制",
    "photo": "照片", "video": "视频", "image": "图片",
    "shouwan": "手腕", "xiaotui": "小腿", "datu": "大腿",
    "qianxiong": "前胸", "hubei": "后背", "yaobu": "腰部", "tunbu": "臀部",
    "jianbu": "肩部", "suogu": "锁骨", "wenhen": "伤痕", "bahen": "疤痕",
    "duanwa": "短袜", "changwa": "长袜", "tuoxie": "拖鞋", "liangxie": "凉鞋",
    "gaogen": "高跟", "yundongxie": "运动鞋", "baixue": "白靴", "heixue": "黑靴",
    "baise": "白色", "heise": "黑色", "hongse": "红色", "lanse": "蓝色",
    "lvse": "绿色", "zise": "紫色", "fense": "粉色", "huangse": "黄色",
    "chengse": "橙色", "zongse": "棕色", "huise": "灰色", "jinse": "金色",
    "yinse": "银色", "shense": "深色", "qianse": "浅色", "touming": "透明",
    "leisi": "蕾丝", "heye": "荷叶", "liubian": "流苏",
}

_SUFFIX_NUM = re.compile(r"^(.*?)(\d+)$")


def _split_translate(k, n=""):
    """组合词拆分：把去分隔符后的词拆成 已知词+已知词(+数字后缀)。"""
    for i in range(len(k) - 1, 0, -1):
        a, b = k[:i], k[i:]
        if a in LABEL_MAP and b in LABEL_MAP:
            return LABEL_MAP[a] + LABEL_MAP[b] + n
    if k in LABEL_MAP:
        return LABEL_MAP[k] + n
    return None


_USER_DICT = None


def _load_user_dict():
    """加载 exe/main.py 同目录的 user_dict.json（用户自定义翻译）。
    返回 {"words": {}, "ignore": [], "case_sensitive": bool}，文件不存在则空字典。"""
    global _USER_DICT
    if _USER_DICT is not None:
        return _USER_DICT
    _USER_DICT = {"words": {}, "ignore": [], "case_sensitive": False}
    try:
        import sys, json as _json
        base = os.path.dirname(os.path.abspath(sys.argv[0]))
        found = False
        for cand in (os.path.join(base, "user_dict.json"),
                     os.path.join(os.getcwd(), "user_dict.json")):
            if os.path.isfile(cand):
                with open(cand, "r", encoding="utf-8") as f:
                    d = _json.load(f)
                if isinstance(d, dict):
                    _USER_DICT["case_sensitive"] = bool(d.get("case_sensitive", False))
                    _USER_DICT["ignore"] = d.get("ignore") or []
                    words = d.get("words") or {}
                    if not _USER_DICT["case_sensitive"]:
                        words = {str(k).lower(): v for k, v in words.items()}
                    _USER_DICT["words"] = words
                found = True
                break
        if not found:
            # 单 exe 用户也能自定义：无词库文件时自动生成模板（空词条不影响运行）
            tpl = {
                "_comment": "自定义翻译词库。words=新增/覆盖翻译(优先于内置)；ignore=保持原样不翻译的后缀；case_sensitive=true 时自定义词区分大小写。_comment 字段程序忽略，不影响运行。",
                "words": {},
                "ignore": [],
                "case_sensitive": False,
            }
            with open(os.path.join(base, "user_dict.json"), "w", encoding="utf-8") as f:
                _json.dump(tpl, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return _USER_DICT


def translate_label(label, lang="zh"):
    """后缀 -> 中文。英文界面(lang!=zh)不翻译；用户词库优先；
    处理下划线/驼峰/大小写拼音/数字后缀/组合词/swap 前缀，未知原样返回。"""
    if lang != "zh":
        return label
    ud = _load_user_dict()
    key = label.lower().strip()
    raw = label.strip()
    # ignore：保持原样不翻译
    if key in ud["ignore"] or raw in ud["ignore"]:
        return label
    # 用户自定义词（优先于内置；case_sensitive 控制是否区分大小写）
    if ud["case_sensitive"]:
        if raw in ud["words"]:
            return ud["words"][raw]
    else:
        if key in ud["words"]:
            return ud["words"][key]
    if key in LABEL_MAP:
        return LABEL_MAP[key]
    key2 = key.replace("_", "").replace("-", "")
    if key2 in LABEL_MAP:
        return LABEL_MAP[key2]
    m = _SUFFIX_NUM.match(key)
    if m and m.group(1) in LABEL_MAP:
        return LABEL_MAP[m.group(1)] + m.group(2)
    if m and m.group(1).replace("_", "") in LABEL_MAP:
        return LABEL_MAP[m.group(1).replace("_", "")] + m.group(2)
    r = _split_translate(key2)
    if r is not None:
        return r
    if m:
        r = _split_translate(m.group(1).replace("_", ""), m.group(2))
        if r is not None:
            return r
    # swap/switch/toggle 前缀显式剥离（SwapNeiku -> 互换内裤）
    base = m.group(1).replace("_", "") if m else key2
    suffix = m.group(2) if m else ""
    for pref, zh in (("swap", "互换"), ("switch", "切换"), ("toggle", "切换")):
        if base.startswith(pref) and len(base) > len(pref):
            rest = base[len(pref):]
            if rest in LABEL_MAP:
                v = LABEL_MAP[rest]
            else:
                v = _split_translate(rest, suffix)
            if v is not None:
                # 剩余部分本身已含"互换/切换"义时不再加前缀（如 TuweiJiaohuan 兔尾互换）
                if "互换" in v or "切换" in v:
                    return v
                return zh + v
    return label


# VK 码转可读按键名（用于记录列表"快捷键"列）
_VK_FRIENDLY = {
    "VK_LEFT": "←", "VK_RIGHT": "→", "VK_UP": "↑", "VK_DOWN": "↓",
    "VK_OEM_2": "/", "VK_OEM_1": ";", "VK_OEM_7": "'", "VK_OEM_3": "`",
    "VK_OEM_4": "[", "VK_OEM_5": "\\", "VK_OEM_6": "]",
    "VK_SPACE": "空格", "VK_RETURN": "回车", "VK_TAB": "Tab", "VK_ESCAPE": "Esc",
    "VK_SHIFT": "Shift", "VK_CONTROL": "Ctrl", "VK_MENU": "Alt", "VK_BACK": "退格",
    "VK_HOME": "Home", "VK_END": "End", "VK_INSERT": "Ins", "VK_DELETE": "Del",
    "VK_PRIOR": "PageUp", "VK_NEXT": "PageDown",
}


def key_display(k):
    """VK_LEFT -> ←；VK_8 -> 8；VK_A -> A；未知原样大写。"""
    k2 = str(k).strip().upper()
    if k2 in _VK_FRIENDLY:
        return _VK_FRIENDLY[k2]
    if k2.startswith("VK_"):
        tail = k2[3:]
        if len(tail) == 1:
            return tail
        if tail == "SPACE":
            return "空格"
        return tail.capitalize()
    return k2


# 候选调出键
_CANDIDATE_KEYS = ["y", "u", "o", "h", "j", "k", "l", "n", "m", "b", "v", "c",
                   "r", "t", "e", "w", "q", "a", "s", "d", "f", "g",
                   "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
                   "VK_OEM_2", "VK_OEM_1", "VK_OEM_7", "VK_OEM_3"]


def pick_toggle_key(used_keys, preferred=None):
    if preferred:
        p = str(preferred).strip()
        if p.lower() not in [k.lower() for k in used_keys]:
            return p
    for k in _CANDIDATE_KEYS:
        if k.lower() not in [u.lower() for u in used_keys]:
            return k
    return "y"


# ---------------- 资源生成 ----------------

_DRAW2D_HLSL = """\
// **** RESPONSIVE UI SHADER ****
// Contributors: SinsOfSeven
// Inspired by VV_Mod_Maker

Texture1D<float4> IniParams : register(t120);

#define SIZE IniParams[87].xy
#define OFFSET IniParams[87].zw

struct vs2ps {
	float4 pos : SV_Position0;
	float2 uv : TEXCOORD1;
};

#ifdef VERTEX_SHADER
void main(
		out vs2ps output,
		uint vertex : SV_VertexID)
{
	float2 BaseCoord,Offset;
	Offset.x = OFFSET.x*2-1;
	Offset.y = (1-OFFSET.y)*2-1;
	BaseCoord.xy = float2((2*SIZE.x),(2*(-SIZE.y)));
	switch(vertex) {
		case 0:
			output.pos.xy = float2(BaseCoord.x+Offset.x, BaseCoord.y+Offset.y);
			output.uv = float2(1,0);
			break;
		case 1:
			output.pos.xy = float2(BaseCoord.x+Offset.x, 0+Offset.y);
			output.uv = float2(1,1);
			break;
		case 2:
			output.pos.xy = float2(0+Offset.x, BaseCoord.y+Offset.y);
			output.uv = float2(0,0);
			break;
		case 3:
			output.pos.xy = float2(0+Offset.x, 0+Offset.y);
			output.uv = float2(0,1);
			break;
		default:
			output.pos.xy = 0;
			output.uv = float2(0,0);
			break;
	};
	output.pos.zw = float2(0, 1);
}
#endif

#ifdef PIXEL_SHADER
Texture2D<float4> tex : register(t100);

void main(vs2ps input, out float4 result : SV_Target0)
{
	float2 dims;
	tex.GetDimensions(dims.x, dims.y);
	if (!dims.x || !dims.y) discard;
	input.uv.y = 1 - input.uv.y;
	result = tex.Load(int3(input.uv.xy*dims.xy, 0));
}
#endif
"""


def _load_font(size):
    from PIL import ImageFont
    for fp in ("C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc",
               "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf",
               "C:/Windows/Fonts/segoeui.ttf"):
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _make_btn(path, text, off):
    """按钮 256x160：半透明深底 + 白细边 + 文字"""
    from PIL import Image, ImageDraw
    w, h, s = 256, 160, 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if off:
        bg, fg, bd = (22, 26, 34, 150), (160, 167, 180, 165), (110, 118, 132, 180)
    else:
        bg, fg, bd = (34, 38, 50, 170), (205, 210, 220, 160), (225, 230, 240, 200)
    d.rounded_rectangle((s, s, w - s, h - s), radius=8 * s, fill=bg, outline=bd, width=2)
    if text:
        size = 62
        font = _load_font(size)
        bbox = font.getbbox(text)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        while (tw > w - 20 or th > h - 16) and size > 16:
            size = int(size * 0.85)
            font = _load_font(size)
            bbox = font.getbbox(text)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text(((w - tw) / 2, (h - th) / 2 - bbox[1]), text, font=font, fill=fg)
    img.save(path, "PNG")


def _make_close(path, color):
    from PIL import Image, ImageDraw
    w, h, s = 96, 96, 3
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((s, s, w - s, h - s), radius=12, fill=(45, 48, 60, 130), outline=color, width=3)
    d.line([(26, 26), (70, 70)], fill=color, width=4)
    d.line([(70, 26), (26, 70)], fill=color, width=4)
    img.save(path, "PNG")


def _set_opacity(im, pct):
    """整体透明度：pct=None 不动；0-100 缩放 alpha"""
    if pct is None:
        return im
    alpha = im.getchannel("A").point(lambda a: max(0, min(255, int(a * pct / 100.0))))
    im.putalpha(alpha)
    return im


def _apply_custom_assets(res_dir, mod_dir, btn_count):
    """检测 mod_dir/zz_panel_custom/：bg.png(背景)、1.png..N.png(按钮图案)、
    opacity.txt(整体透明度 0-100)。存在则替换默认生成的资源（自动缩放适配预设尺寸）。"""
    if not mod_dir or not os.path.isdir(mod_dir):
        return
    cust = os.path.join(mod_dir, "zz_panel_custom")
    if not os.path.isdir(cust):
        return
    from PIL import Image
    resample = getattr(Image, "LANCZOS", None) or getattr(getattr(Image, "Resampling", None), "LANCZOS")
    op = None
    op_path = os.path.join(cust, "opacity.txt")
    if os.path.isfile(op_path):
        try:
            op = float(io.open(op_path, encoding="utf-8").read().strip())
        except Exception:
            op = None
    bg = os.path.join(cust, "bg.png")
    if os.path.isfile(bg):
        try:
            im = Image.open(bg).convert("RGBA").resize((512, 256), resample)
            im = _set_opacity(im, op)
            im.save(os.path.join(res_dir, "panel_bg.png"), "PNG")
        except Exception:
            pass
    for i in range(1, btn_count + 1):
        src = os.path.join(cust, "%d.png" % i)
        if not os.path.isfile(src):
            continue
        try:
            im = Image.open(src).convert("RGBA").resize((256, 160), resample)
            im = _set_opacity(im, op)
            im.save(os.path.join(res_dir, "btn_%d.png" % i), "PNG")
            off_op = (op if op is not None else 100) * 0.5
            off = _set_opacity(im.copy(), off_op)
            off.save(os.path.join(res_dir, "btn_%d_off.png" % i), "PNG")
        except Exception:
            pass


def generate_assets(res_dir, buttons, method, labels, mod_dir=None):
    """生成 draw_2d.hlsl + 背景 + 关闭 + 按钮 PNG。labels = [显示文字]。
    mod_dir 非空时检测 zz_panel_custom 用自定义图片替换默认资源。"""
    os.makedirs(res_dir, exist_ok=True)
    with open(os.path.join(res_dir, "draw_2d.hlsl"), "w", encoding="utf-8", newline="\n") as f:
        f.write(_DRAW2D_HLSL)
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (512, 256), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle(
        (4, 4, 508, 252), radius=20, fill=(30, 34, 46, 110),
        outline=(150, 160, 190, 120), width=2)
    img.save(os.path.join(res_dir, "panel_bg.png"), "PNG")
    _make_close(os.path.join(res_dir, "close.png"), (210, 216, 228, 180))
    _make_close(os.path.join(res_dir, "close_hover.png"), (255, 120, 120, 220))
    for i, txt in enumerate(labels, start=1):
        _make_btn(os.path.join(res_dir, "btn_%d.png" % i), txt, off=False)
        _make_btn(os.path.join(res_dir, "btn_%d_off.png" % i), txt, off=True)
    _apply_custom_assets(res_dir, mod_dir, len(labels))
    return


# ---------------- 注入式面板段生成 ----------------

def _fmt_val(v):
    v = v.strip()
    if v.isdigit():
        return v
    try:
        f = float(v)
        if f == int(f):
            return str(int(f))
        return repr(round(f, 5))
    except Exception:
        return v


def build_injection(ini_path, buttons, method, mod_name, toggle_key, layout, detect=None):
    """生成注入式面板段文本（样式1 验收结构：单 hold 段 + 增量式拖动）"""
    n = len(buttons)
    cols = layout["cols"]
    bw, bh = layout["bw"], layout["bh"]
    gap, pad, title_h, close_w = layout["gap"], layout["pad"], layout["title_h"], layout["close_w"]
    pw, ph = layout["pw"], layout["ph"]
    bx0, by0 = layout.get("bx0", pad), layout.get("by0", title_h + pad)
    rows = math.ceil(n / cols)

    L = []
    L.append("")
    L.append(PANEL_MARK + " (generated by WWMI MOD Panel Helper)")
    L.append("[Constants]")
    L.append("global $zz_open = 0")
    L.append("global $zz_clicked = 0")
    L.append("global $zz_holded = 0")
    L.append("global $zz_drag = 0")
    L.append("global $zz_cx = 0")
    L.append("global $zz_cy = 0")
    L.append("global $zz_lastx = 0")
    L.append("global $zz_lasty = 0")
    if detect and detect.get("kind") == "self":
        L.append("global $zz_detected = 0")
    L.append("global $zz_ww = 1920")
    L.append("global $zz_wh = 1080")
    L.append("global $zz_ar = 1.7778")
    L.append("global $zz_fx = %s" % _fmt_val(str(layout["fx"])))
    L.append("global $zz_fy = %s" % _fmt_val(str(layout["fy"])))
    L.append("global $zz_bw = %s" % _fmt_val(str(bw)))
    L.append("global $zz_bh = %s" % _fmt_val(str(bh)))
    L.append("global $zz_gap = %s" % _fmt_val(str(gap)))
    L.append("global $zz_pad = %s" % _fmt_val(str(pad)))
    L.append("global $zz_title_h = %s" % _fmt_val(str(title_h)))
    L.append("global $zz_close_w = %s" % _fmt_val(str(close_w)))
    L.append("global $zz_bx0 = %s" % _fmt_val(str(bx0)))
    L.append("global $zz_by0 = %s" % _fmt_val(str(by0)))
    L.append("global $zz_cols = %d" % cols)
    L.append("global $zz_btns = %d" % n)
    L.append("global $zz_pw = %s" % _fmt_val(str(pw)))
    L.append("global $zz_ph = %s" % _fmt_val(str(ph)))
    L.append("")
    L.append("[KeyToggleZZUI]")
    if detect:
        if detect.get("kind") == "reuse":
            L.append("condition = %s" % detect["cond"])
        elif detect.get("kind") == "self":
            L.append("condition = $zz_detected == 1")
    L.append("key = %s" % toggle_key)
    L.append("type = cycle")
    L.append("$zz_open = 0, 1")
    L.append("")
    L.append("[KeyMouseZZ]")
    L.append("condition = $zz_open")
    L.append("key = VK_LBUTTON")
    L.append("type = hold")
    L.append("$zz_holded = 1")
    L.append("$zz_clicked = 1")
    L.append("")
    L.append("[Present]")
    if detect and detect.get("kind") == "self":
        L.append("post $zz_detected = 0")
    L.append("if $zz_open")
    L.append("    run = CommandListZZInit")
    L.append("    run = CommandListZZDraw")
    L.append("    $zz_clicked = 0")
    L.append("endif")
    L.append("")
    L.append("[CommandListZZInit]")
    L.append("if window_width >= 640")
    L.append("    $zz_ww = window_width")
    L.append("    $zz_wh = window_height")
    L.append("else if rt_width >= 640")
    L.append("    $zz_ww = rt_width")
    L.append("    $zz_wh = rt_height")
    L.append("else")
    L.append("    $zz_ww = res_width")
    L.append("    $zz_wh = res_height")
    L.append("endif")
    L.append("$zz_ar = $zz_ww / $zz_wh")
    L.append("if cursor_x > 0 && cursor_y > 0 && cursor_x < 1 && cursor_y < 1")
    L.append("    $zz_cx = cursor_x")
    L.append("    $zz_cy = cursor_y")
    L.append("else if cursor_window_x > 0 && cursor_window_y > 0 && cursor_window_x < $zz_ww && cursor_window_y < $zz_wh")
    L.append("    $zz_cx = cursor_window_x / $zz_ww")
    L.append("    $zz_cy = cursor_window_y / $zz_wh")
    L.append("else")
    L.append("    $zz_cx = cursor_screen_x / $zz_ww")
    L.append("    $zz_cy = cursor_screen_y / $zz_wh")
    L.append("endif")
    L.append("")
    L.append("[CommandListZZDraw]")
    L.append("x87 = $zz_pw")
    L.append("y87 = $zz_ph * $zz_ar")
    L.append("z87 = $zz_fx")
    L.append("w87 = $zz_fy")
    L.append("ps-t100 = ResourceZZBg")
    L.append("run = CustomShaderElementZZ")
    L.append("run = CommandListZZClose")
    for i in range(1, n + 1):
        L.append("run = CommandListZZBtn%d" % i)
    L.append("run = CommandListZZDrag")
    L.append("")

    for i in range(1, n + 1):
        idx = i - 1
        col = idx % cols
        row = idx // cols
        bx = "$zz_fx + $zz_bx0 + %d * ($zz_bw + $zz_gap)" % col
        by = "$zz_fy + ($zz_by0 + %d * ($zz_bh + $zz_gap)) * $zz_ar" % row
        L.append("[CommandListZZBtn%d]" % i)
        L.append("if $zz_cy > %s && $zz_cy < %s + $zz_bh * $zz_ar" % (by, by))
        L.append("    if $zz_cx > %s && $zz_cx < %s + $zz_bw" % (bx, bx))
        L.append("        if $zz_clicked")
        L.append("            run = CommandListZZToggle%d" % i)
        L.append("        endif")
        L.append("    endif")
        L.append("endif")
        if len(buttons[idx]["values"]) == 2:
            L.append("if %s == %s" % (_vref(buttons[idx]), _fmt_val(buttons[idx]["values"][0])))
            L.append("    ps-t100 = ResourceZZBtn%d_off" % i)
            L.append("else")
            L.append("    ps-t100 = ResourceZZBtn%d" % i)
            L.append("endif")
        else:
            L.append("ps-t100 = ResourceZZBtn%d" % i)
        L.append("x87 = $zz_bw")
        L.append("y87 = $zz_bh * $zz_ar")
        L.append("z87 = %s" % bx)
        L.append("w87 = %s" % by)
        L.append("run = CustomShaderElementZZ")
        L.append("")

    for i, btn in enumerate(buttons, start=1):
        vals = btn["values"]
        L.append("[CommandListZZToggle%d]" % i)
        L.append("; %s  key = %s" % (btn["name"], btn["key"]))
        # 去重保序，保证 if/else 分支无重复条件
        uniq = []
        for v in vals:
            if v not in uniq:
                uniq.append(v)
        nv = len(uniq)
        for j in range(nv):
            nxt = uniq[(j + 1) % nv]
            prefix = "if" if j == 0 else "else if"
            L.append("%s %s == %s" % (prefix, _vref(btn), _fmt_val(uniq[j])))
            L.append("    %s = %s" % (_vref(btn), _fmt_val(nxt)))
        L.append("endif")
        L.append("")

    L.append("[CommandListZZClose]")
    L.append("if $zz_cy > $zz_fy && $zz_cy < $zz_fy + $zz_title_h * $zz_ar")
    L.append("    if $zz_cx > $zz_fx + $zz_pw - $zz_close_w && $zz_cx < $zz_fx + $zz_pw")
    L.append("        if $zz_clicked")
    L.append("            $zz_open = 0")
    L.append("        endif")
    L.append("        ps-t100 = ResourceZZCloseHover")
    L.append("    else")
    L.append("        ps-t100 = ResourceZZClose")
    L.append("    endif")
    L.append("else")
    L.append("    ps-t100 = ResourceZZClose")
    L.append("endif")
    L.append("x87 = $zz_close_w")
    L.append("y87 = $zz_title_h * $zz_ar")
    L.append("z87 = $zz_fx + $zz_pw - $zz_close_w")
    L.append("w87 = $zz_fy")
    L.append("run = CustomShaderElementZZ")
    L.append("")

    L.append("[CommandListZZDrag]")
    L.append("if $zz_drag")
    L.append("    if $zz_holded")
    L.append("        $zz_fx = $zz_fx + ($zz_cx - $zz_lastx)")
    L.append("        $zz_fy = $zz_fy + ($zz_cy - $zz_lasty)")
    L.append("    else")
    L.append("        $zz_drag = 0")
    L.append("    endif")
    L.append("else if $zz_holded")
    L.append("    if $zz_cy > $zz_fy && $zz_cy < $zz_fy + $zz_title_h * $zz_ar")
    L.append("        if $zz_cx > $zz_fx && $zz_cx < $zz_fx + $zz_pw")
    L.append("            $zz_drag = 1")
    L.append("        endif")
    L.append("    endif")
    L.append("endif")
    L.append("if $zz_fx < 0")
    L.append("    $zz_fx = 0")
    L.append("endif")
    L.append("if $zz_fx + $zz_pw > 1")
    L.append("    $zz_fx = 1 - $zz_pw")
    L.append("endif")
    L.append("if $zz_fy < 0")
    L.append("    $zz_fy = 0")
    L.append("endif")
    L.append("if $zz_fy + $zz_ph * $zz_ar > 1")
    L.append("    $zz_fy = 1 - $zz_ph * $zz_ar")
    L.append("endif")
    L.append("$zz_lastx = $zz_cx")
    L.append("$zz_lasty = $zz_cy")
    L.append("")

    L.append("[CustomShaderElementZZ]")
    L.append("hs = null")
    L.append("ds = null")
    L.append("gs = null")
    L.append("cs = null")
    L.append("vs = .\\%s\\draw_2d.hlsl" % PANEL_RES)
    L.append("ps = .\\%s\\draw_2d.hlsl" % PANEL_RES)
    L.append("blend = ADD SRC_ALPHA INV_SRC_ALPHA")
    L.append("cull = none")
    L.append("topology = triangle_strip")
    L.append("o0 = set_viewport bb")
    L.append("Draw = 4,0")
    L.append("")
    L.append("[ResourceZZBg]")
    L.append("filename = .\\%s\\panel_bg.png" % PANEL_RES)
    L.append("")
    L.append("[ResourceZZClose]")
    L.append("filename = .\\%s\\close.png" % PANEL_RES)
    L.append("")
    L.append("[ResourceZZCloseHover]")
    L.append("filename = .\\%s\\close_hover.png" % PANEL_RES)
    L.append("")
    for i in range(1, n + 1):
        L.append("[ResourceZZBtn%d]" % i)
        L.append("filename = .\\%s\\btn_%d.png" % (PANEL_RES, i))
        L.append("")
        L.append("[ResourceZZBtn%d_off]" % i)
        L.append("filename = .\\%s\\btn_%d_off.png" % (PANEL_RES, i))
        L.append("")
    if detect and detect.get("kind") == "self":
        L.append("[TextureOverrideZZDetect]")
        L.append("hash = %s" % detect["hash"])
        if detect.get("match_first_index"):
            L.append("match_first_index = %s" % detect["match_first_index"])
        L.append("$zz_detected = 1")
        L.append("")
    return "\n".join(L)


def make_layout(n, layout_override=None):
    """计算布局。override 支持：bw/bh/gap/pad/title_h/close_w/fx/fy/cols/
    pw_scale（背景放大系数，自定义注入用）、fill（True=按钮放大铺满背景）。
    普通注入：按钮区正好铺满背景（bx0=pad）；自定义不勾选填充：按钮默认大小、
    按钮区在放大后的背景内居中（长方形包长方形）。"""
    cols = _cols_for(n)
    bw = layout_override.get("bw", DEF_BW) if layout_override else DEF_BW
    bh = layout_override.get("bh", DEF_BH) if layout_override else DEF_BH
    gap = layout_override.get("gap", DEF_GAP) if layout_override else DEF_GAP
    pad = layout_override.get("pad", DEF_PAD) if layout_override else DEF_PAD
    title_h = layout_override.get("title_h", DEF_TITLE_H) if layout_override else DEF_TITLE_H
    close_w = layout_override.get("close_w", DEF_CLOSE_W) if layout_override else DEF_CLOSE_W
    fx = layout_override.get("fx", DEF_FX) if layout_override else DEF_FX
    fy = layout_override.get("fy", DEF_FY) if layout_override else DEF_FY
    if layout_override and layout_override.get("cols"):
        cols = int(layout_override["cols"])
    rows = math.ceil(n / cols)
    pw_scale = (layout_override.get("pw_scale") or 1.0) if layout_override else 1.0
    fill = bool(layout_override.get("fill")) if layout_override else False
    area_w = cols * bw + (cols - 1) * gap
    area_h = rows * bh + (rows - 1) * gap
    pw = (pad * 2 + area_w) * pw_scale
    ph = (title_h + pad + area_h) * pw_scale
    custom = bool(layout_override) and pw_scale != 1.0
    if fill:
        bw2 = (pw - 2 * pad - (cols - 1) * gap) / cols
        bh2 = (ph - title_h - pad - (rows - 1) * gap) / rows
        bx0, by0 = pad, title_h + pad
    elif custom:
        bw2, bh2 = bw, bh
        bx0 = (pw - area_w) / 2
        by0 = (ph - title_h - area_h) / 2 + title_h
    else:
        bw2, bh2 = bw, bh
        bx0, by0 = pad, title_h + pad
    return {"cols": cols, "bw": bw2, "bh": bh2, "gap": gap, "pad": pad,
            "title_h": title_h, "close_w": close_w, "pw": pw, "ph": ph,
            "bx0": bx0, "by0": by0, "fx": fx, "fy": fy}


def _detect_info(ini_path):
    """返回面板调出键的人物在场检测方案（社区同款机制）：
      reuse: 复用 mod 已有检测变量（该变量确有置位赋值，如 $active = 1）
      self:  工具自建 TextureOverride 检测段（同 hash 命中人物网格 -> $zz_detected = 1）
      none:  无可用方案（退回无 condition）
    """
    try:
        with open(ini_path, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
    except Exception:
        return {"kind": "none"}
    base = txt.split(PANEL_MARK, 1)[0]
    # 1) mod 第一个 Key 段的 condition 变量，且该变量有置位赋值
    for m in re.finditer(r"(?m)^\[([^\]]+)\][^\[]*", base):
        name = m.group(1)
        if not name.startswith("Key"):
            continue
        if name.startswith("KeyMouse") or name.startswith("KeyToggleZZUI"):
            continue
        sec = m.group(0)
        cm = re.search(r"(?m)^\s*condition\s*=\s*(.+?)\s*$", sec)
        if not cm:
            continue
        expr = cm.group(1).strip()
        vm = re.search(r"\$([A-Za-z_][A-Za-z0-9_]*)", expr)
        if not vm or "zz_" in vm.group(1):
            continue
        var = "$" + vm.group(1)
        set_hits = re.findall(r"(?m)^\s*" + re.escape(var) + r"\s*=\s*([^;\s]+)", base)
        set_vals = [v for v in set_hits if v != "0"]
        if set_vals:
            return {"kind": "reuse", "cond": expr}
    # 2) 自建：优先人物组件网格段（TextureOverrideComponentN），
    #    退而求其次任意 TextureOverride（含 hash 的）
    for pattern in (r"(?m)^\[TextureOverrideComponent[^\]]*\][^\[]*",
                    r"(?m)^\[TextureOverrideUIMenu[^\]]*\][^\[]*",
                    r"(?m)^\[TextureOverride[^\]]*\][^\[]*"):
        for m in re.finditer(pattern, base):
            sec = m.group(0)
            hm = re.search(r"(?m)^\s*hash\s*=\s*([0-9a-fA-Fx]+)", sec)
            if hm:
                info = {"kind": "self", "hash": hm.group(1)}
                fm = re.search(r"(?m)^\s*match_first_index\s*=\s*(\d+)", sec)
                if fm:
                    info["match_first_index"] = fm.group(1)
                return info
    return {"kind": "none"}


def _labels_path(ini_path):
    return os.path.join(os.path.dirname(ini_path), LABELS_FILE)


def _res_dir(ini_path):
    return os.path.join(os.path.dirname(ini_path), PANEL_RES)


def save_labels(ini_path, data):
    import json
    with open(_labels_path(ini_path), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_labels(ini_path):
    import json
    p = _labels_path(ini_path)
    if not os.path.isfile(p):
        return None
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def read_panel_toggle_key(ini_path):
    """从已注入的 ini 读取 [KeyToggleZZUI] 的 key（面板调出键）"""
    try:
        with open(ini_path, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
    except Exception:
        return ""
    m = re.search(r"\[KeyToggleZZUI\][^\[]*?key\s*=\s*([^\s;]+)", txt, re.I | re.S)
    return m.group(1) if m else ""


def scan_panels(root):
    """递归扫描根目录，找出所有已注入面板的 ini（含 PANEL_MARK），
    返回可重建 history 的记录列表（按 mod 目录去重）。"""
    records = []
    if not root or not os.path.isdir(root):
        return records
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if not fn.lower().endswith(".ini"):
                continue
            ini = os.path.join(dirpath, fn)
            try:
                with open(ini, "r", encoding="utf-8", errors="ignore") as f:
                    if PANEL_MARK not in f.read():
                        continue
            except Exception:
                continue
            bak = ""
            try:
                for bfn in sorted(os.listdir(dirpath)):
                    if bfn.startswith(fn + ".") and bfn.endswith(".bak_panel"):
                        bak = os.path.join(dirpath, bfn)
                        break
            except Exception:
                pass
            n = 0
            try:
                data = load_labels(ini)
                if data:
                    n = len(data.get("labels", []))
            except Exception:
                pass
            records.append({
                "mod_path": dirpath,
                "mod_name": os.path.basename(dirpath),
                "ini_path": ini,
                "bak_path": bak,
                "method": "SCAN",
                "button_count": n,
                "toggle_key": read_panel_toggle_key(ini),
                "key_summary": "",
                "time": "",
                "ts": 0.0,
            })
    seen = set()
    out = []
    for r in records:
        if r["mod_path"] in seen:
            continue
        seen.add(r["mod_path"])
        out.append(r)
    return out


def find_injected_ini(mod_dir):
    """在 mod 目录找已注入面板的 ini（含 PANEL_MARK）"""
    for ini in _find_inis(mod_dir):
        try:
            with open(ini, "r", encoding="utf-8", errors="ignore") as f:
                if PANEL_MARK in f.read():
                    return ini
        except Exception:
            continue
    return None


def recommend_ini(buttons):
    """多 ini 时的注入目标推荐：默认命名空间优先、按钮数多优先。
    返回 (推荐ini, [(ini, 按钮数, namespace, 得分), ...])"""
    from collections import Counter
    cnt = Counter(b.get("src") for b in buttons)
    ns_map = {}
    for b in buttons:
        ns_map[b["src"]] = (b.get("ns") or "")
    info = []
    best, best_score = None, -1
    for ini, c in cnt.items():
        ns = ns_map.get(ini, "")
        score = c * 10
        if ns:
            score -= 15          # 面板放进 namespace ini 会连累 zz_* 变量与跨 ns 引用
        else:
            score += 20          # 默认命名空间：面板 + Toggle 最稳妥
        info.append((ini, c, ns, score))
        if score > best_score:
            best, best_score = ini, score
    info.sort(key=lambda x: -x[3])
    return best, info


def inject_panel(ini_path, buttons, method, mod_name, toggle_key, layout=None, lang="zh"):
    """备份 -> 追加面板段 -> 生成资源 -> 写 labels.json（失败自动回滚）"""
    n = len(buttons)
    if n == 0:
        raise ValueError("no buttons")
    lay = layout or make_layout(n)
    with open(ini_path, "r", encoding="utf-8", errors="ignore") as f:
        src = f.read()
    if PANEL_MARK in src:
        raise FileExistsError("panel already injected")

    # 清理同 ini 的旧面板备份（防堆积；新备份=当前版本）
    try:
        fn = os.path.basename(ini_path)
        d = os.path.dirname(ini_path)
        for bfn in os.listdir(d):
            if bfn.startswith(fn + ".") and bfn.endswith(".bak_panel"):
                os.remove(os.path.join(d, bfn))
    except Exception:
        pass
    bak = ini_path + "." + time.strftime("%Y%m%d%H%M%S") + ".bak_panel"
    shutil.copy2(ini_path, bak)

    try:
        if method == 1:
            labels = [translate_label(b["label"], lang) for b in buttons]
        else:
            labels = [str(i) for i in range(1, n + 1)]

        text = build_injection(ini_path, buttons, method, mod_name, toggle_key, lay,
                               detect=_detect_info(ini_path))
        with open(ini_path, "r", encoding="utf-8", errors="ignore") as f:
            src = f.read()
        with open(ini_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(src.rstrip() + "\n" + text + "\n")

        generate_assets(_res_dir(ini_path), buttons, method, labels, os.path.dirname(ini_path))
        save_labels(ini_path, {
            "ini": os.path.basename(ini_path),
            "mod_name": mod_name,
            "method": method,
            "toggle_key": toggle_key,
            "labels": labels,
            "buttons": [{"var": b["var"], "label": b["label"], "key": b["key"],
                         "values": b["values"]} for b in buttons],
            "layout": lay,
        })
        return bak
    except Exception:
        rollback(ini_path, bak)
        raise


def _extract_panel_text(src):
    """从 ini 文本提取面板段（从 PANEL_MARK 到结尾）"""
    idx = src.find(PANEL_MARK)
    if idx < 0:
        return None
    return src[idx:]


def read_layout_from_ini(ini_path):
    """从注入的 ini 读面板布局参数"""
    with open(ini_path, "r", encoding="utf-8", errors="ignore") as f:
        src = f.read()
    seg = _extract_panel_text(src)
    if seg is None:
        return None
    lay = {}
    for m in re.finditer(r"^global \$zz_(bw|bh|gap|pad|title_h|close_w|cols|btns|pw|ph|fx|fy)\s*=\s*([\d.]+)$",
                         seg, re.M):
        lay[m.group(1)] = float(m.group(2))
    return lay or None


def rebuild_and_replace(ini_path, layout):
    """用新布局重新生成面板段并替换（读 labels.json 重建）"""
    data = load_labels(ini_path)
    if data is None:
        raise FileNotFoundError("labels file missing")
    buttons = []
    for b in data["buttons"]:
        buttons.append({"name": "Key" + b["var"].lstrip("$"), "label": b["label"],
                        "key": b.get("key", ""), "type": "cycle", "var": b["var"],
                        "values": b["values"]})
    text = build_injection(ini_path, buttons, data["method"], data["mod_name"],
                           data["toggle_key"], layout, detect=_detect_info(ini_path))
    with open(ini_path, "r", encoding="utf-8", errors="ignore") as f:
        src = f.read()
    idx = src.find(PANEL_MARK)
    if idx < 0:
        raise FileExistsError("panel not injected")
    base = src[:idx].rstrip()
    with open(ini_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(base + "\n" + text + "\n")
    data["layout"] = layout
    save_labels(ini_path, data)
    return layout


def adjust(ini_path, action):
    """右键调整：bigger/smaller/taller/wider/reset"""
    lay = read_layout_from_ini(ini_path)
    if lay is None:
        raise FileNotFoundError("panel not injected")
    bw, bh = lay["bw"], lay["bh"]
    if action == "bigger":
        bw, bh = bw + 0.005, bh + 0.004
    elif action == "smaller":
        bw, bh = max(0.03, bw - 0.005), max(0.02, bh - 0.004)
    elif action == "taller":
        bh = bh + 0.004
    elif action == "wider":
        bw = bw + 0.004
    elif action == "reset":
        bw, bh = DEF_BW, DEF_BH
    else:
        raise ValueError(action)
    new_lay = make_layout(int(lay["btns"]), dict(lay, bw=bw, bh=bh))
    new_lay["fx"], new_lay["fy"] = lay.get("fx", DEF_FX), lay.get("fy", DEF_FY)
    rebuild_and_replace(ini_path, new_lay)
    return new_lay


def apply_labels(ini_path, new_labels):
    """改字：更新 labels -> 重新生成按钮 PNG + 更新 labels.json"""
    data = load_labels(ini_path)
    if data is None:
        raise FileNotFoundError("labels file missing")
    if len(new_labels) != len(data["labels"]):
        raise ValueError("label count mismatch")
    data["labels"] = new_labels
    n = len(new_labels)
    res_dir = _res_dir(ini_path)
    for i, txt in enumerate(new_labels, start=1):
        _make_btn(os.path.join(res_dir, "btn_%d.png" % i), txt, off=False)
        _make_btn(os.path.join(res_dir, "btn_%d_off.png" % i), txt, off=True)
    _apply_custom_assets(res_dir, os.path.dirname(ini_path), n)
    save_labels(ini_path, data)
    return data["labels"]


def rollback(ini_path, bak_path):
    """回滚：优先用时间最早的备份恢复 ini；删除该 ini 的全部面板备份与生成物
    （zz_panel_res / zz_panel_labels.json / zz_panel_custom 自定义图片），做到无注入痕迹。"""
    d = os.path.dirname(ini_path)
    fn = os.path.basename(ini_path)
    baks = sorted(bfn for bfn in os.listdir(d)
                  if bfn.startswith(fn + ".") and bfn.endswith(".bak_panel"))
    if not baks and os.path.isfile(bak_path):
        baks = [os.path.basename(bak_path)]
    if not baks:
        raise FileNotFoundError("no panel backup for " + ini_path)
    # 恢复时间最早的备份（文件名时间戳字典序即时间序，最早在前）
    src = os.path.join(d, baks[0])
    shutil.copy2(src, ini_path)
    # 删除该 ini 全部面板备份（多余备份一并清掉）
    for b in baks:
        try:
            os.remove(os.path.join(d, b))
        except Exception:
            pass
    # 清理生成物
    res_dir = _res_dir(ini_path)
    if os.path.isdir(res_dir):
        for f in os.listdir(res_dir):
            try:
                os.remove(os.path.join(res_dir, f))
            except Exception:
                pass
        try:
            os.rmdir(res_dir)
        except Exception:
            pass
    lp = _labels_path(ini_path)
    if os.path.isfile(lp):
        try:
            os.remove(lp)
        except Exception:
            pass
    # 清理自定义图片文件夹（回滚后不留注入痕迹）
    cust = os.path.join(d, "zz_panel_custom")
    if os.path.isdir(cust):
        shutil.rmtree(cust, ignore_errors=True)
    return True
