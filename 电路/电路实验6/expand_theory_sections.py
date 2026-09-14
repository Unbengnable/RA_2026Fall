from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).parent


def set_font(run):
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    run.font.size = Pt(10.5)


def add_before(anchor, content):
    """Insert a normal body paragraph directly before anchor, without changing existing text."""
    p_element = OxmlElement("w:p")
    anchor._p.addprevious(p_element)
    p = Paragraph(p_element, anchor._parent)
    p.paragraph_format.line_spacing = 1.35
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.first_line_indent = Cm(0.74)
    run = p.add_run(content)
    set_font(run)


def expand(path, theory_heading, next_heading, paragraphs):
    doc = Document(path)
    ps = doc.paragraphs
    if any("【原理扩展】" in p.text for p in ps):
        print("already expanded:", path)
        return
    begin = next((i for i,p in enumerate(ps) if p.text.strip() == theory_heading), None)
    end = next((i for i,p in enumerate(ps) if i > begin and p.text.strip() == next_heading), None)
    if begin is None or end is None:
        raise ValueError(f"Could not locate theory section in {path}")
    anchor = ps[end]
    # Insert in natural order, always immediately before the next heading.
    for item in paragraphs:
        add_before(anchor, item)
    doc.save(path)
    print("expanded:", path)


expand(
    ROOT / "实验六 基尔霍夫定律验证实验报告.docx",
    "三、实验原理", "四、实验电路、节点与参考方向",
    [
        "【原理扩展】KCL的物理基础是电荷守恒。对一个足够小的节点区域，在稳态直流条件下，节点中不发生净电荷积累，因此流入与流出的电荷量在任意时段内相等。写方程前先任意规定各支路电流参考方向；计算结果为正表示实际方向与假定一致，结果为负则说明实际方向相反。",
        "KVL的物理基础是能量守恒。沿闭合路径绕行一周，单位电荷因电源获得的能量与在电阻等元件上损失或储存/释放的能量代数和为零。在本实验的直流电阻网络中，电阻电压满足u=Ri；穿越电源由“−”到“+”记为电压上升，穿越电阻沿电流方向记为电压降，只要符号约定前后一致，均可得到等价方程。",
        "实验验证不要求代数残差严格等于零，而以残差相对于相关电压或电流量级的比例来判断一致性。残差主要来自元件允差、仪表分辨率、表内阻、接触电阻和电源带载波动；因此应将测得方向、量程和有效数字与计算式一并记录，避免把方向或单位错误误判为定律不成立。",
    ],
)

expand(
    ROOT / "实验1-2" / "实验一 元件伏安特性测量实验报告.docx",
    "二、实验原理", "三、实验电路与仪器",
    [
        "【原理扩展】对线性电阻，在温度近似恒定且处于额定工作范围内，端电压与电流满足U=RI。若以U为横轴、I为纵轴，图线为通过原点的直线，斜率为1/R；若以I为横轴、U为纵轴，斜率为R。正、反向同时测得的直线应关于原点对称，这是无方向线性元件的重要判据。",
        "二极管和发光二极管属于PN结非线性元件。正向偏置时，低电压区电流很小，超过导通区后电流迅速增加；反向偏置时仅有很小的反向漏电流，未达到击穿电压前不应出现显著反向电流。发光二极管的正向压降通常高于普通硅二极管，且其测试支路中的限流电阻会共同决定外部测得的U–I曲线斜率。",
        "两种伏安法的误差可由仪表内阻解释：电流表外接时，电压表测得的是被测电阻与电流表的总压降，所得电阻偏大；电压表外接时，电流表读到被测电阻电流与电压表分流电流之和，所得电阻偏小。因而小电阻宜优先采用电流表外接法，大电阻宜优先采用电压表外接法。",
    ],
)

expand(
    ROOT / "实验1-2" / "实验二 电位电压测定与电位图实验报告.docx",
    "二、实验原理", "三、实验电路与仪器",
    [
        "【原理扩展】电位不是节点自身的绝对属性，而是相对于选定参考点的电压。若参考点由O改为O′，所有节点电位会统一平移同一常数，即VA′=VA−VO′；但任意两节点的电压UAB=VA−VB不变。因此，电位图必须明确零电位参考点，而支路电压的判定不依赖参考点选择。",
        "用电压表测电位时，应将负表笔固定接在参考点、正表笔接被测节点，表的正负读数直接给出该节点的电位。测量UAB时，正表笔接A、负表笔接B，故读数对应VA−VB。若读数为负，说明A点实际电位低于B点，而不是仪表失效。",
        "将各相邻支路电压按闭合回路顺序相加，可写成Uab+Ubc+…+Uga=0；这是KVL在电位表示下的直接结果，因为相邻电位差逐项相加会首尾相消。等电位点之间U=0，理想短接不会产生支路电流，也不改变其余网络的节点电位；实验中的微小变化反映电位器调节精度和仪表分辨率。",
    ],
)
