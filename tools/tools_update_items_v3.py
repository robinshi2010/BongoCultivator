import sqlite3
import json
import os

DB_PATH = 'user_data.db'

# Data definition
# Format: ID, Name, Type, Description
TIER_ITEMS = {
    0: [
        ("herb_marrow_0", "洗髓草", "Spirit", "叶脉呈半透明蓝色，如同微型血管般搏动，能剥离骨骼中的凡俗杂质。"),
        ("flower_blood_0", "凝血花", "Spirit", "生长在兽冢之上的猩红花朵，散发着令人不适的铁锈腥气。"),
        ("fruit_fire_0", "赤焰果", "Spirit", "表皮粗糙温热，咬开后会有滚烫的汁液溅射，是提炼火灵气的初级媒介。"),
        ("ore_iron_essence", "百炼铁精", "Mineral", "凡铁经千次锻打后留下的核心，表面有天然生成的云纹。"),
        ("part_wolf_tooth", "妖狼断齿", "Monster", "依然残留着嗜血本能的断齿，靠近皮肤会感到轻微刺痛。"),
        ("misc_talisman_old", "褪色的符纸", "Junk", "一张绘制失败的聚气符，朱砂已化为黑灰，毫无灵力波动。"),
        ("misc_broken_sword", "断裂凡剑", "Junk", "缺口处崩裂严重，显然是与硬物剧烈碰撞的结果。"),
        ("herb_ghost_vine", "鬼枯藤", "Spirit", "生长在阴暗地穴，触感冰凉如尸体皮肤，常用于中和丹毒。"),
        ("water_dew_morning", "无根晨露", "Liquid", "未落地便被收集的露水，纯净无垢，是调和药性的良溶剂。"),
        ("part_bat_wing", "夜魔翼膜", "Monster", "薄如蝉翼但坚韧异常，对着光看能看到细密的黑色神经网。"),
    ],
    1: [
        ("herb_dragon_1", "龙纹草", "Spirit", "叶片上有金色纹路游走，仿佛封印了一条微型金龙。"),
        ("ore_cold_crystal", "寒潭晶石", "Mineral", "即使在烈日下也散发着刺骨寒意，周围空气会凝结出白霜。"),
        ("part_spider_silk", "人面蛛丝", "Monster", "坚韧得可以切断钢铁，丝线上附着着令人致幻的神经毒素。"),
        ("fruit_thunder_1", "雷浆果", "Spirit", "果实内部有电弧跳动，吞服时舌尖会有强烈的麻痹感。"),
        ("earth_milk", "大地石乳", "Liquid", "万年岩层滴落的乳白色液体，一滴重达千钧。"),
        ("ore_copper_red", "赤铜精母", "Mineral", "通体赤红，敲击时会发出金石之音，是炼制法器的上佳材料。"),
        ("part_snake_skin", "灵蛇蜕", "Monster", "完整的蛇蜕，鳞片依然保持着活性，会随环境变色。"),
        ("herb_illusory", "幻心兰", "Spirit", "长时间注视花蕊会产生坠入深渊的错觉。"),
        ("misc_jade_broken", "碎裂玉简", "Junk", "记录功法的玉片，可惜关键部分已经粉碎。"),
        ("misc_beast_bone", "不明兽骨", "Junk", "经历岁月侵蚀已看不出原形，但依旧坚硬如铁。"),
    ],
    2: [
        ("herb_purple_mky", "紫猴花", "Spirit", "花瓣酷似鬼脸猴，晨昏时分会发出尖锐的啼哭声。"),
        ("wood_sky_thunder", "天雷竹", "Material", "通体焦黑但生机勃勃，只生长在雷击最密集的山巅。"),
        ("ore_star_sand", "星辰砂", "Mineral", "每一粒沙都极其沉重，仿佛是天上星辰的残骸。"),
        ("part_turtle_shell", "玄龟甲片", "Monster", "背负洛书纹路，据说能用来推演天机。"),
        ("beast_core_gold", "金丹妖核", "Monster", "妖兽一身精华所在，表面流转着复杂的妖力回路。"),
        ("water_glacier", "万年冰魄", "Material", "永不融化的深蓝色冰块，能冻结修士的神识。"),
        ("herb_fire_lotus", "地心火莲", "Spirit", "根系扎根于岩浆之中，花瓣由纯粹的火元素构成。"),
        ("misc_array_flag", "破损阵旗", "Junk", "虽然旗面残破，但旗杆仍有微弱的灵力反应。"),
        ("misc_alchemy_ash", "炸炉灰烬", "Junk", "炼丹失败后的产物，依稀能分辨出原本昂贵的药材。"),
        ("fruit_soul_2", "养魂木果", "Spirit", "果皮呈灰白色，贴在额头能滋养受损的神魂。"),
    ],
    3: [
        ("herb_soul_restore", "九曲灵参", "Spirit", "已具备初级灵智，出土便会化作白兔逃遁，需用红绳束缚。"),
        ("ore_void_stone", "虚空石", "Mineral", "没有固定形状，视线穿过它会看到扭曲的空间波纹。"),
        ("part_dragon_scale", "亚龙逆鳞", "Monster", "含有稀薄真龙血脉，触碰时会感到威严的龙吟压迫。"),
        ("water_nether", "黄泉鬼水", "Liquid", "来自幽冥界的浑浊河水，能腐蚀修士的法宝灵光。"),
        ("wood_parasol", "凤栖梧桐", "Material", "传说中凤凰栖息的古木，自带一种令人心安的暖意。"),
        ("herb_nirvana", "涅槃花", "Spirit", "枯荣循环极快，一天之内经历发芽到枯萎的全部过程。"),
        ("part_phoenix_fthr", "火凤尾羽", "Material", "即使脱落本体，依然燃烧着永不熄灭的虚幻火焰。"),
        ("misc_ancient_map", "古修遗图", "Junk", "兽皮绘制的地图，标注的山川地貌与现今完全不同。"),
        ("ore_meteor_iron", "天外陨铁", "Mineral", "不属于这个世界的金属，对灵气的传导率是普通金属的百倍。"),
        ("fruit_five_color", "五彩莲子", "Spirit", "同时散发五行灵气，极其罕见。"),
    ],
    4: [
        ("ore_sky_crystal_sand", "天晶沙", "Mineral", "散发着极光般的色彩，每一粒都像是一个微缩的小世界。"),
        ("part_kunpeng_feather", "鲲鹏真羽", "Material", "不知其几千里也，仅仅一根羽毛就需要纳戒百丈空间才能装下。"),
        ("soil_chaos", "混沌息壤", "Material", "一粒尘埃便重如山岳，能自我生长，是祭炼洞天福地的基石。"),
        ("herb_spirit_fly", "化灵草", "Spirit", "草叶如同飞鸟般在空中盘旋，拥有自主意识，极难捕捉。"),
        ("water_heavy_yuan", "一元重水", "Liquid", "至阴至寒，一滴可化沧海，能压碎普通的空间戒指。"),
        ("fruit_law", "道果雏形", "Spirit", "表面有天然形成的道纹，直视它会感到头晕目眩，仿佛看到了规则的线条。"),
        ("beast_core_void", "虚空兽核", "Monster", "半透明的内丹，握在手中感觉手掌部分消失在了异次元。"),
        ("misc_broken_divine", "残破神器", "Junk", "上古神战遗留的兵器碎片，虽然威能尽失，但材质坚不可摧。"),
    ],
    5: [
        ("metal_taiyi", "太乙精金", "Mineral", "金之本源，由于密度过大，连光线经过它附近都会发生扭曲。"),
        ("dust_void", "虚空之尘", "Material", "从空间裂缝中扫出的尘埃，没有任何重量，却能吞噬灵识。"),
        ("fungus_heaven", "补天芝", "Spirit", "传说中女娲补天遗留的灵种，拥有修复世界法则的能力。"),
        ("core_star", "死星之核", "Material", "冷却后的恒星核心，内部依然封印着恐怖的热核能量。"),
        ("part_void_dragon", "太虚龙爪", "Monster", "游弋于世界间隙的巨兽之爪，指尖时刻切割着细小的空间裂缝。"),
        ("flower_other_shore", "彼岸花", "Spirit", "开在生与死、真实与虚幻的交界处，花香能唤醒前世记忆。"),
        ("misc_world_frag", "世界碎片", "Junk", "一个已经毁灭的小世界的残片，里面或许封印着未知的文明遗迹。"),
    ],
    6: [
        ("horn_true_dragon", "真龙之角", "Material", "真正的九天真龙之角，仅仅放置在那里，万兽便不敢靠近。"),
        ("bone_kirin_arm", "麒麟臂骨", "Monster", "蕴含祥瑞与毁灭双重力量的臂骨，是炼体的终极素材。"),
        ("fruit_yin_yang", "阴阳双生果", "Spirit", "一半极黑，一半极白，完美的阴阳平衡，可塑造混沌之体。"),
        ("water_creation", "造化神泉", "Liquid", "据说能点化顽石，赋予死物灵智。"),
        ("stone_three_life", "三生石", "Mineral", "照见前世、今生、来世，是参悟因果法则的媒介。"),
        ("wood_world_tree", "建木枝桠", "Material", "传说中连接天地的神树断枝，拥有打通两界通道的能力。"),
    ],
    7: [
        ("sand_time", "光阴之沙", "Mineral", "握在手中，你会看到指尖的皮肤快速老化又重生。"),
        ("thread_karma", "因果线", "Material", "看不见但摸得到，仿佛某种坚韧的丝线，连接着万事万物的命运。"),
        ("leaf_world_tree", "世界树叶", "Spirit", "一片叶子就是一个宇宙，脉络展示了星系的运行轨迹。"),
        ("blood_ancestor", "祖巫精血", "Monster", "开天劈地之初诞生的生灵之血，蕴含创世法则碎片。"),
        ("crystal_origin", "本源结晶", "Material", "这个位面最核心的能源，通过它能直接与天道对话。"),
    ],
    8: [
        ("liquid_thunder", "天劫雷液", "Liquid", "渡劫成功后，劫云消散时滴落的金色液体，蕴含毁灭与新生。"),
        ("frag_heaven_way", "天道碎片", "Material", "天道崩塌后散落的规则碎片，凡人不可直视。"),
        ("lotus_chaos", "混沌青莲", "Spirit", "在宇宙大爆炸前的混沌中绽放的莲花，万宝之祖。"),
        ("gas_primordial", "鸿蒙紫气", "Special", "成圣之基，宇宙中最原始的一缕气机。"),
        ("stone_destiny", "定界石", "Mineral", "能够稳定一个位面的基石，用来抵御飞升通道的时空风暴。"),
    ],
    9: [
        ("guide_light_gold", "接引金光", "Material", "来自上界的指引之光。"),
        ("item_the_key", "仙界通行证", "Special", "通往更高维度的钥匙。"),
        ("pen_author", "作者的钢笔", "Special", "这只钢笔似乎拥有改写现实的能力。"),
    ]
}

# Pills & Recipes
# Format: ID, Name, Type, Description, Ingredients{id: count}
# Price is auto-calculated based on tier. Exp/Effect logic handled in code, here we just define metadata.
TIER_PILLS = {
    0: [
        ("pill_gather_qi", "聚气散", "Exp", "粗糙的粉末状药剂，入口极苦，强行扩充经脉以容纳灵气。", {"herb_marrow_0": 3, "water_dew_morning": 1}),
        ("pill_body_basic", "壮骨丸", "Stat", "混合了兽骨粉的黑色药丸，大幅增强肌肉密度。", {"part_wolf_tooth": 2, "ore_iron_essence": 1}),
        ("pill_speed_wind", "疾风散", "Buff", "服下后双腿轻盈如风，感觉不到重力的束缚。", {"part_bat_wing": 2, "herb_marrow_0": 1}),
        ("pill_detox_0", "避毒珠", "Utility", "含在口中可过滤瘴气，探险必备。", {"herb_ghost_vine": 2, "water_dew_morning": 2}),
        ("pill_break_found", "筑基辅药", "Break", "一碗浓稠的汤药，散发着令人心悸的灵压，是突破凡体的催化剂。", {"flower_blood_0": 5, "fruit_fire_0": 2, "ore_iron_essence": 1}),
    ],
    1: [
        ("pill_base_liquid", "培元丹", "Exp", "圆润的白色丹药，温和地滋养液态真元。", {"herb_dragon_1": 3, "earth_milk": 1}),
        ("pill_mind_calm", "定神丹", "Recov", "清凉之气直冲天灵，平复体内躁动的元素乱流。", {"herb_illusory": 2, "ore_cold_crystal": 1}),
        ("pill_strength_bary", "大地金刚丸", "Stat", "皮肤泛起金属光泽，短时间内力量暴增。", {"ore_copper_red": 2, "part_spider_silk": 5}),
        ("pill_vis_night", "夜视散", "Utility", "涂抹眼部，黑暗视物如同白昼。", {"part_snake_skin": 1, "herb_illusory": 1}),
        ("pill_break_gold", "结金丹", "Break", "丹成龙虎现，金色的丹晕仿佛要吞噬周围的光线。", {"fruit_thunder_1": 5, "part_snake_skin": 2, "ore_copper_red": 1}),
    ],
    2: [
        ("pill_gold_dew", "黄龙丹", "Exp", "金黄剔透，入口即化，庞大的药力如黄河决堤般冲刷经脉。", {"herb_purple_mky": 3, "herb_fire_lotus": 1}),
        ("pill_beauty_face", "定颜丹", "Cosmetic", "虽然对修为无益，但能将容貌永远定格在服用的一刻。", {"water_glacier": 1, "herb_purple_mky": 1, "part_spider_silk": 5}),
        ("pill_crazy_blood", "燃血丹", "Buff", "透支生命潜能换取短暂的爆发力，副作用极大。", {"beast_core_gold": 1, "herb_fire_lotus": 2}),
        ("pill_break_soul", "凝婴丹", "Break", "丹药内部仿佛有一个婴儿在呼吸，是破丹成婴的关键。", {"fruit_soul_2": 3, "water_glacier": 2, "part_turtle_shell": 1}),
        ("pill_luck_minor", "小气运丹", "Buff", "短暂蒙蔽天机，此时开箱、掉落会有意想不到的好运。", {"herb_purple_mky": 2, "ore_star_sand": 1}),
    ],
    3: [
        ("pill_purple_gold", "紫金丹", "Exp", "紫气东来，金光内敛，专补元婴本源。", {"fruit_five_color": 3, "herb_nirvana": 1}),
        ("pill_soul_protect", "护神丹", "Recov", "在识海中形成一道屏障，抵御心魔入侵。", {"herb_soul_restore": 1, "wood_parasol": 1}),
        ("pill_teleport", "缩地成寸符", "Utility", "吞服后可瞬间移动（极高闪避）。", {"ore_void_stone": 2, "part_bat_wing": 10}),
        ("pill_break_god", "化神丹", "Break", "服下后会感到灵魂脱壳，直面天地法则的威压。", {"part_dragon_scale": 1, "ore_meteor_iron": 2, "herb_nirvana": 1}),
        ("pill_clone_shadow", "身外化身丹", "Special", "制造一个拥有本体30%实力的幻影协助战斗。", {"herb_soul_restore": 1, "water_nether": 2}),
    ],
    4: [
        ("pill_wonder_10k", "万妙丹", "Exp", "包含了万种草木精华，吞服后仿佛经历了万次枯荣轮回。", {"herb_spirit_fly": 3, "fruit_law": 1}),
        ("pill_break_law", "破法丹", "Special", "服用后短时间内无视一切法则压制。", {"beast_core_void": 1, "misc_broken_divine": 1}),
        ("pill_soul_field", "元神养道丹", "Recov", "滋养刚刚诞生的元神领域，使其更加稳固。", {"fruit_law": 1, "water_heavy_yuan": 1}),
        ("pill_break_void", "炼虚丹", "Break", "服用后肉身开始虚化，开始尝试与虚空同频率震动。", {"ore_sky_crystal_sand": 1, "water_heavy_yuan": 1, "soil_chaos": 1}),
    ],
    5: [
        ("pill_great_void", "太虚丹", "Exp", "丹药呈灰色漩涡状，入口即是虚无，直接补充本源损耗。", {"dust_void": 5, "metal_taiyi": 1}),
        ("pill_reborn_heaven", "回天再造丸", "Recov", "只要元神不灭，肉身化为灰烬亦可瞬间重聚。", {"fungus_heaven": 1, "flower_other_shore": 1}),
        ("pill_dimension_step", "界游丹", "Buff", "短时间内完全融入虚空，不受任何物理干涉。", {"part_void_dragon": 1, "dust_void": 2}),
        ("pill_break_fusion", "合体丹", "Break", "让肉身与元神完美融合，不分彼此。", {"part_void_dragon": 1, "core_star": 1, "dust_void": 3}),
    ],
    6: [
        ("pill_fusion_grand", "合体大丹", "Exp", "每一颗都需要在圣火中煅烧千年，药力浩瀚如海。", {"wood_world_tree": 1, "water_creation": 2}),
        ("pill_nine_cycle", "九转金丹", "Special", "丹成九转，鬼神皆惊，拥有起死人肉白骨的逆天功效。", {"fruit_yin_yang": 1, "water_creation": 3}),
        ("pill_body_saint", "圣体丹", "Stat", "将肉身强度提升至圣境，单凭肉体力量即可撕裂虚空。", {"bone_kirin_arm": 1, "horn_true_dragon": 1}),
        ("pill_break_maha", "大乘丹", "Break", "感悟圆满，从有限走向无限。", {"fruit_yin_yang": 2, "stone_three_life": 1, "wood_world_tree": 1}),
    ],
    7: [
        ("pill_mahayana_gold", "无量金丹", "Exp", "无量光，无量寿，蕴含无法计算的庞大修为。", {"leaf_world_tree": 3, "crystal_origin": 1}),
        ("pill_time_back", "回溯丹", "Utility", "能将自身状态回溯到10秒之前，堪称后悔药。", {"sand_time": 3, "thread_karma": 1}),
        ("pill_long_life", "长生丹", "Special", "服用后寿元无尽，心魔不再滋生，真正的大逍遥。", {"leaf_world_tree": 1, "blood_ancestor": 1}),
        ("pill_break_trib", "渡劫丹", "Break", "为最后的天劫做准备，凝聚全身精气神于一点。", {"blood_ancestor": 1, "thread_karma": 3, "crystal_origin": 1}),
    ],
    8: [
        ("pill_anti_thunder", "避雷丹", "Buff", "欺骗天机，使天劫威力削弱三层，渡劫成功率大幅提升。", {"lotus_chaos": 1, "frag_heaven_way": 1}),
        ("pill_ascension_fake", "飞升丹", "Special", "虽然名字叫飞升丹，但其实是让人在不飞升的情况下拥有仙人法力。", {"gas_primordial": 1, "stone_destiny": 1}),
        ("pill_final_destiny", "终极造化丹", "Exp", "凡界炼丹术的尽头，吞服一颗便可抵万年苦修。", {"liquid_thunder": 1, "lotus_chaos": 1, "gas_primordial": 1}),
    ]
}

def update_database():
    print("Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Clear tables
    print("Clearing old definitions and recipes...")
    cursor.execute("DELETE FROM item_definitions")
    cursor.execute("DELETE FROM recipes")
    
    # 2. Insert Items
    print("Inserting new items...")
    item_count = 0
    
    # Helper for price calc (Exponential)
    def get_price(tier):
        return 100 * (4 ** tier) 

    # Insert Items
    for tier, items in TIER_ITEMS.items():
        base_price = get_price(tier)
        for item_data in items:
            iid, name, itype, desc = item_data
            
            # Simple pricing logic
            price = base_price
            if itype == "Junk": price //= 2
            if itype == "Mineral": price *= 1.5
            if itype == "Monster": price *= 2
            if itype == "Special": price *= 10
            
            cursor.execute(
                "INSERT INTO item_definitions (id, name, type, tier, description, price, effect_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (iid, name, itype.lower(), tier, desc, int(price), "{}")
            )
            item_count += 1

    # Insert Pills (which are also items)
    for tier, pills in TIER_PILLS.items():
        base_price = get_price(tier)
        for pill_data in pills:
            iid, name, ptype, desc, _ = pill_data
            
            # Pill metadata
            price = base_price * 5 # Pills are expensive
            effect_type = ptype.lower()
            
            # Rough effect logic JSON
            effect = {}
            if "Exp" in ptype:
                effect["exp_gain"] = 0.05 * (tier + 1) # dummy, actual logic is in code
            if "Break" in ptype:
                effect["breakthrough_chance"] = 0.2
                
            cursor.execute(
                "INSERT INTO item_definitions (id, name, type, tier, description, price, effect_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (iid, name, ptype.lower(), tier, desc, int(price), json.dumps(effect))
            )
            item_count += 1

    # 3. Insert Recipes
    print("Inserting recipes...")
    recipe_count = 0
    for tier, pills in TIER_PILLS.items():
        for pill_data in pills:
            iid, _, _, _, ingredients = pill_data
            
            cursor.execute(
                "INSERT INTO recipes (result_item_id, ingredients_json, craft_time, success_rate) VALUES (?, ?, ?, ?)",
                (iid, json.dumps(ingredients), 10, 0.8)
            )
            recipe_count += 1

    conn.commit()
    conn.close()
    print(f"Update complete. Inserted {item_count} items and {recipe_count} recipes.")

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
    else:
        update_database()
