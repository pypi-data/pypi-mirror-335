import os
from dvatioff_audio.utils import retry, get_wav_path_in_folder
from lxml import etree
from tqdm import tqdm


@retry(Exception, tries=10, delay=1)
def get_connected_project_name_info(client):
    """
    获取当前 Wwise 工程名称
    """
    try:
        result_wwise_version = client.call("ak.wwise.core.getInfo")
        result_project_name = client.call("ak.wwise.core.object.get", {"from": {"ofType": ["Project"]}})

        if 'version' in result_wwise_version and 'return' in result_project_name:
            wwise_version = result_wwise_version['version']['displayName'].replace("v", "Wwise ")
            project_name = result_project_name['return'][0]['name']
            print(f"成功获取项目信息: {project_name} - {wwise_version}")
            return project_name, wwise_version
        else:
            raise ValueError("获取项目信息失败： Wwise Authoring 可能正在初始化...")
    except Exception as e:
        print(f"调用 ak.wwise.core.getProjectInfo 时出错: {e}")
        raise


@retry(Exception, tries=10, delay=1)
def get_object(client, object_path):
    """
    获取 Wwise 对象信息
    """
    try:
        args = {
            "from": {
                "path": [object_path]
            }
        }
        result = client.call("ak.wwise.core.object.get", args)
        return result
    except Exception as e:
        print(f"调用 ak.wwise.core.object.get 时出错: {e}")
        return None


@retry(Exception, tries=10, delay=1)
def get_object_waql(client, waql):
    """
    使用 WAQL 获取 Wwise 对象信息
    """
    try:
        args = {
            "waql": waql
        }
        result = client.call("ak.wwise.core.object.get", args)
        return result
    except Exception as e:
        print(f"调用 ak.wwise.core.object.get 时出错: {e}")
        return None


@retry(Exception, tries=10, delay=1)
def get_selected_objects(client):
    """
    获取当前 Wwise 工程选中的对象
    """
    try:
        opts = {
            "return": [
                "id",
                "name",
                "type",
                "path",
                "RandomOrSequence",
            ]
        }
        result = client.call("ak.wwise.ui.getSelectedObjects", options=opts)
        if 'objects' in result:
            # 分离 RandomOrSequence 类型
            for obj in result['objects']:
                if 'RandomOrSequence' in obj:
                    obj['type'] = 'SequenceContainer' if obj['RandomOrSequence'] == 0 else 'RandomContainer'
            return result
        else:
            return None
    except Exception as e:
        print(f"调用 ak.wwise.ui.getSelectedObjects 时出错: {e}")
        return None


@retry(Exception, tries=10, delay=1)
def create_object(client, object_type, parent_path, object_name, on_name_conflict="merge", children=None, output_bus=None, makeup_gain=None, priority=None, enable_hdr_envelope=None):
    """
    创建 Wwise 对象
    """
    try:
        args = {
            "parent": parent_path,
            "type": object_type,
            "name": object_name,
            "onNameConflict": on_name_conflict,
        }
        if children:
            args["children"] = children
        if output_bus:
            args["@OutputBus"] = output_bus
            args['@OverrideOutput'] = True
        if makeup_gain:
            args["@MakeUpGain"] = makeup_gain
        if priority:
            args["@Priority"] = priority
            args["@OverridePriority"] = True
        if enable_hdr_envelope:
            args["@OverrideHdrEnvelope"] = True
            args["@HdrEnableEnvelope"] = True
            args["@HdrEnvelopeSensitivity"] = 9
        result = client.call("ak.wwise.core.object.create", args)
        return result
    except Exception as e:
        print(f"调用 ak.wwise.core.object.create 时出错: {e}")
        return None


@retry(Exception, tries=10, delay=1)
def set_object(client, objects):
    """
    设置 Wwise 对象属性
    """
    try:
        args = {
            "objects": []
        }
        for obj in objects:
            arg = {}
            for key, value in obj.items():
                arg[key] = value
            args["objects"].append(arg)
        result = client.call("ak.wwise.core.object.set", args)
        return result
    except Exception as e:
        print(f"调用 ak.wwise.core.object.setProperty 时出错: {e}")
        return None


@retry(Exception, tries=10, delay=1)
def set_soundbank_inclusion(client, soundbank, obj, operation="add", inclusions_filter=None):
    """
    设置 SoundBank 包含的对象
    """
    try:
        if inclusions_filter is None:
            inclusions_filter = [
                "events",
                "structures",
                "media"
            ]
        args = {
            "soundbank": soundbank,
            "operation": operation,
            "inclusions": [
                {
                    "object": obj,
                    "filter": inclusions_filter
                }
            ]
        }
        result = client.call("ak.wwise.core.soundbank.setInclusions", args)
        return result
    except Exception as e:
        print(f"调用 ak.wwise.core.soundbank.setInclusions 时出错: {e}")
        return None


@retry(Exception, tries=10, delay=1)
def import_audio_file(client, **kwargs):
    """
    导入音频文件到 Wwise
    """
    try:
        args = {
            "importOperation": "useExisting",
            "default": {
                "importLanguage": kwargs.get("importLanguage", "")
            },
            "imports": [
                {
                    "audioFile": kwargs.get("audioFile", ""),
                    "originalsSubFolder": kwargs.get("originalsSubFolder", ""),
                    "objectPath": kwargs.get("objectPath", "")
                }
            ]
        }
        if kwargs.get("isLoopingEnabled", False):
            args["imports"][0]["@IsLoopingEnabled"] = True
        if kwargs.get("notes", ""):
            args["imports"][0]["notes"] = kwargs.get("notes", "")
        result = client.call("ak.wwise.core.audio.import", args)
        return result
    except Exception as e:
        print(f"调用 ak.wwise.core.audio.import 时出错: {e}")
        return None


@retry(Exception, tries=10, delay=1)
def get_wwise_originals_sfx_path(client):
    """
    获取 Wwise Originals SFX 文件夹的路径
    """
    try:
        result = client.call("ak.wwise.core.getProjectInfo")
        if 'directories' in result:
            originals_path = result['directories']['originals']
            return os.path.join(originals_path, "SFX")
        else:
            raise ValueError("获取 Wwise Originals SFX 文件夹路径失败")
    except Exception as e:
        print(f"调用 ak.wwise.core.getProjectInfo 时出错: {e}")
        return None


@retry(Exception, tries=10, delay=1)
def get_wwise_originals_path(client):
    """
    获取 Wwise Originals 文件夹路径
    """
    try:
        result = client.call("ak.wwise.core.getProjectInfo")
        if 'directories' in result:
            originals_path = result['directories']['originals']
            return originals_path
        else:
            raise ValueError("获取 Wwise Originals 文件夹路径失败")
    except Exception as e:
        print(f"调用 ak.wwise.core.getProjectInfo 时出错: {e}")
        return None


@retry(Exception, tries=10, delay=1)
def add_switch_assignment(client, child, stateOrSwitch):
    """
    添加 Switch Assignment
    """
    try:
        args = {
            "child": child,
            "stateOrSwitch": stateOrSwitch
        }
        result = client.call("ak.wwise.core.switchContainer.addAssignment", args)
        return result
    except Exception as e:
        print(f"调用 ak.wwise.core.switchContainer.addAssignment 时出错: {e}")
        return None


@retry(Exception, tries=10, delay=1)
def copy_object(client, obj, parent, on_name_conflict="rename"):
    """
    复制 Wwise 对象
    """
    try:
        args = {
            "object": obj,
            "parent": parent,
            "onNameConflict": on_name_conflict
        }
        result = client.call("ak.wwise.core.object.copy", args)
        return result
    except Exception as e:
        print(f"调用 ak.wwise.core.object.copy 时出错: {e}")
        return None


@retry(Exception, tries=10, delay=1)
def move_object(client, obj, parent, on_name_conflict="rename"):
    """
    移动 Wwise 对象
    """
    try:
        args = {
            "object": obj,
            "parent": parent,
            "onNameConflict": on_name_conflict
        }
        result = client.call("ak.wwise.core.object.move", args)
        return result
    except Exception as e:
        print(f"调用 ak.wwise.core.object.move 时出错: {e}")
        return None


@retry(Exception, tries=10, delay=1)
def set_name(client, obj, name):
    """
    设置 Wwise 对象名称
    """
    try:
        args = {
            "object": obj,
            "value": name
        }
        result = client.call("ak.wwise.core.object.setName", args)
        return result
    except Exception as e:
        print(f"调用 ak.wwise.core.object.setName 时出错: {e}")
        return None


@retry(Exception, tries=10, delay=1)
def set_notes(client, obj, notes):
    """
    设置 Wwise 对象备注
    """
    try:
        args = {
            "object": obj,
            "value": notes
        }
        result = client.call("ak.wwise.core.object.setNotes", args)
        return result
    except Exception as e:
        print(f"调用 ak.wwise.core.object.setNotes 时出错: {e}")
        return None


@retry(Exception, tries=10, delay=1)
def delete_object(client, obj):
    """
    删除 Wwise 对象
    """
    try:
        args = {
            "object": obj
        }
        result = client.call("ak.wwise.core.object.delete", args)
        return result
    except Exception as e:
        print(f"调用 ak.wwise.core.object.delete 时出错: {e}")
        return None


# 下面的函数无需连接 waapi 即可调用
def assign_obj_to_dynamic_event_path(container_dict, dynamic_event_wwu_path, wwu_guid):
    """
    由于 waapi 无法直接为 Dynamic Event 中的各 path 指定对象，因此需要通过解析 Wwise Work Unit 文件来实现
    在指定规则下为 Dynamic Event 中的各 path 指定对象
    """
    tree = etree.parse(dynamic_event_wwu_path)
    root = tree.getroot()
    total_iterations = len(container_dict.keys())
    with tqdm(total=total_iterations, desc="Adding Dynamic Path") as pbar:
        for multi_switch_entry in root.findall('.//MultiSwitchEntry'):
            pbar.update(1)
            state_tuple = ()
            for obj in multi_switch_entry.iterfind('.//ObjectRef'):
                state_tuple += (obj.get('Name'),)

            obj_id = container_dict[state_tuple]
            obj_name = f"Hit_{state_tuple[0]}_{state_tuple[1]}_{state_tuple[2]}_{state_tuple[3]}"
            reference_list = etree.SubElement(multi_switch_entry, "ReferenceList")
            reference = etree.SubElement(reference_list, "Reference", Name='AudioNode')
            object_ref = etree.SubElement(reference, "ObjectRef", Name=obj_name, ID=obj_id, WorkUnitID=wwu_guid)

            object_lists = multi_switch_entry.find('.//ObjectLists')

            index = list(multi_switch_entry).index(object_lists)
            multi_switch_entry.insert(index, reference_list)

    tree.write(dynamic_event_wwu_path, pretty_print=True)


def match_replaced_audios(client, folder_path):
    """
    遍历给定文件夹中的 .wav 文件，搜索 Originals 文件夹中的同名文件，返回匹配和不匹配的文件的路径
    """
    matched_files = []
    unmatched_files = []
    path_originals = get_wwise_originals_sfx_path(client)
    new_wav_path = get_wav_path_in_folder(folder_path)
    ori_wav_path = get_wav_path_in_folder(path_originals)

    for key, value in new_wav_path.items():
        if key in ori_wav_path.keys():
            matched_files.append([value, ori_wav_path[key]])
        else:
            root = os.path.dirname(value)
            unmatched_files.append([root, key])

    if unmatched_files:
        return matched_files, unmatched_files, ori_wav_path
    else:
        return matched_files, None, None
