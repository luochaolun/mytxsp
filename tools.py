import yaml

yaml_path = "./config.yaml"

def write_yaml(r):
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(r, f)

def read_yaml():
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.load(f, Loader=yaml.FullLoader)

def updata_yaml(k, v):
    old_data = read_yaml()
    old_data[k] = v
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(old_data, f)

def get_config():
    try:
        data = read_yaml()
    except FileNotFoundError:
        tx = input("请输入腾讯cookie：")
        data = {
            "txck": tx,
        }
        write_yaml(data)
    return data

def djb2Hash(e):
    t = 5381
    for r in range(len(e)):
        t += (t << 5) + ord(e[r])
    return t & 2147483647

def dealck(ck: str) -> dict:
    ck = ck.split(";")
    ckdict = {}
    for i in ck:
        i = i.strip()
        i = i.split("=")
        ckdict[i[0]] = i[1]
    return ckdict
