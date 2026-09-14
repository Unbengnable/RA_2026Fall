from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import pypdfium2 as pdfium
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

ROOT = Path(__file__).parent
OUTDIR = ROOT / "实验1-2"
TEMPLATE = ROOT / "电路技术基础（上）实验报告模板.docx"


def font(run, size=10.5, bold=False):
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    run.font.size = Pt(size)
    run.bold = bold


def borders(table):
    pr = table._tbl.tblPr
    bs = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement("w:" + edge)
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "6"); e.set(qn("w:color"), "808080")
        bs.append(e)
    pr.append(bs)


def text(doc, s, size=10.5, bold=False, align=None, indent=True, after=3):
    p = doc.add_paragraph(); p.paragraph_format.line_spacing = 1.35; p.paragraph_format.space_after = Pt(after)
    if indent: p.paragraph_format.first_line_indent = Cm(.74)
    if align is not None: p.alignment = align
    r = p.add_run(s); font(r, size, bold)
    return p


def heading(doc, s, level=1):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(10 if level == 1 else 6); p.paragraph_format.space_after = Pt(5); p.paragraph_format.keep_with_next = True
    r = p.add_run(s); font(r, 14 if level == 1 else 12, True)
    return p


def figure(doc, file, caption, width=12.8):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(file), width=Cm(width))
    text(doc, caption, 9.5, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, after=6)


def table(doc, headers, rows):
    tb = doc.add_table(rows=1, cols=len(headers)); tb.alignment = WD_TABLE_ALIGNMENT.CENTER; borders(tb)
    for c, v in zip(tb.rows[0].cells, headers):
        c.text=v; c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
        shade=OxmlElement("w:shd"); shade.set(qn("w:fill"), "D9EAF7"); c._tc.get_or_add_tcPr().append(shade)
        for r in c.paragraphs[0].runs: font(r, 9.5, True)
        c.paragraphs[0].alignment=WD_ALIGN_PARAGRAPH.CENTER
    for vals in rows:
        cells=tb.add_row().cells
        for c,v in zip(cells, vals):
            c.text=str(v); c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for p in c.paragraphs:
                p.paragraph_format.space_after=Pt(1)
                for r in p.runs: font(r, 9.3)
    doc.add_paragraph().paragraph_format.space_after=Pt(1)


def placeholder(doc, name):
    tb=doc.add_table(rows=1, cols=1); tb.alignment=WD_TABLE_ALIGNMENT.CENTER; borders(tb)
    c=tb.cell(0,0); c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    sh=OxmlElement("w:shd"); sh.set(qn("w:fill"), "F2F2F2"); c._tc.get_or_add_tcPr().append(sh)
    p=c.paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(24); p.paragraph_format.space_after=Pt(24)
    r=p.add_run(f"【待插入：{name}】\n请粘贴原始手写数据照片，确保量程、单位、正负号清晰。"); font(r,10.5)


def delete_body_after(p):
    parent=p._element.getparent(); on=False
    for c in list(parent):
        if on and c.tag != qn("w:sectPr"): parent.remove(c)
        if c is p._element: on=True


def new_doc(title):
    d=Document(str(TEMPLATE)); ps=d.paragraphs
    ps[2].text="实验报告"
    for r in ps[2].runs: font(r,22,True)
    ps[10].text="实验名称："+title; ps[11].text="实验日期：________________"; ps[12].text="指导教师：黄毅刚老师"
    for i in (10,11,12):
        for r in ps[i].runs: font(r,12)
    delete_body_after(ps[14]); d.add_page_break()
    sec=d.sections[0]; sec.top_margin=Cm(2.2); sec.bottom_margin=Cm(2.2); sec.left_margin=Cm(2.5); sec.right_margin=Cm(2.5)
    return d


def render_crops():
    # Experiment 1: Figure 4, two meter connections.
    p1=pdfium.PdfDocument(str(OUTDIR/"电路原理实验指导书_25-28.pdf"))[2].render(scale=3).to_pil()
    p1.crop((260,225,1270,660)).save(OUTDIR/"实验1_伏安法接线.png")
    # Experiment 2: Figures 1 and 2 (reference-point circuits), and 3/4 (equal potential).
    p2=pdfium.PdfDocument(str(OUTDIR/"电路原理实验指导书_29-32.pdf"))[1].render(scale=3).to_pil()
    p2.crop((190,1150,1370,1695)).save(OUTDIR/"实验2_参考点电路.png")
    p3=pdfium.PdfDocument(str(OUTDIR/"电路原理实验指导书_29-32.pdf"))[2].render(scale=3).to_pil()
    p3.crop((200,410,1370,1010)).save(OUTDIR/"实验2_等电位电路.png")


def chart(path, x, y, xlabel, ylabel, title, color):
    """Dependency-free, high-resolution line chart rendered with Pillow."""
    w,h=1260,825; left,right,top,bottom=150,70,100,125
    im=Image.new("RGB",(w,h),"white"); draw=ImageDraw.Draw(im)
    regular=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",26)
    small=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",21)
    bold=ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf",30)
    xmin,xmax=min(x),max(x); ymin,ymax=min(y),max(y)
    if xmin==xmax: xmax=xmin+1
    if ymin==ymax: ymax=ymin+1
    padx=(xmax-xmin)*.06 or 1; pady=(ymax-ymin)*.12 or 1
    xmin-=padx; xmax+=padx; ymin-=pady; ymax+=pady
    pw,ph=w-left-right,h-top-bottom
    sx=lambda v:left+(v-xmin)/(xmax-xmin)*pw
    sy=lambda v:top+(ymax-v)/(ymax-ymin)*ph
    # grid and ticks
    for j in range(6):
        xx=left+j*pw/5; yy=top+j*ph/5
        draw.line((xx,top,xx,top+ph),fill="#D9D9D9",width=1)
        draw.line((left,yy,left+pw,yy),fill="#D9D9D9",width=1)
        xv=xmin+j*(xmax-xmin)/5; yv=ymax-j*(ymax-ymin)/5
        draw.text((xx-18,top+ph+12),f"{xv:.1f}",fill="#333333",font=small)
        draw.text((25,yy-11),f"{yv:.3g}",fill="#333333",font=small)
    draw.line((left,top,left,top+ph),fill="#222222",width=3); draw.line((left,top+ph,left+pw,top+ph),fill="#222222",width=3)
    pts=[(sx(a),sy(b)) for a,b in zip(x,y)]
    draw.line(pts,fill=color,width=5)
    for px,py in pts: draw.ellipse((px-7,py-7,px+7,py+7),fill="white",outline=color,width=4)
    draw.text((w//2-250,25),title,fill="#111111",font=bold)
    draw.text((w//2-65,h-70),xlabel,fill="#111111",font=regular)
    draw.text((20,55),ylabel,fill="#111111",font=regular)
    im.save(path)


def make_charts():
    # The last four tables in the provided record: D4 LED, two connections, forward/reverse.
    i=list(range(0,11)); u13=[0,2.859,3.91,4.95,5.98,6.99,8.03,9.04,10.04,11.05,12.06]
    u15=[0,2.85,3.91,4.95,5.99,7.01,8.05,9.07,10.10,11.12,12.14]
    ur=list(range(0,21,2)); ir14=[0,.001,.001,.001,.001,.001,.001,.002,.002,.002,.002]
    ir16=[0,.001,.001,.001,.001,.001,.001,.001,.001,.001,.001]
    chart(OUTDIR/"实验1_附表13_D4正向.png",i,u13,"I (mA)","U (V)","D4 forward characteristic — Table 13","#1565C0")
    chart(OUTDIR/"实验1_附表14_D4反向.png",ur,ir14,"U_R (V)","I_R (µA)","D4 reverse characteristic — Table 14","#C45508")
    chart(OUTDIR/"实验1_附表15_D4正向.png",i,u15,"I (mA)","U (V)","D4 forward characteristic — Table 15","#2E8B57")
    chart(OUTDIR/"实验1_附表16_D4反向.png",ur,ir16,"U_R (V)","I_R (µA)","D4 reverse characteristic — Table 16","#7A3E9D")
    # Potential diagram for experiment 2, using e as the zero-potential reference.
    w,h=1260,700; left,right,top,bottom=105,65,85,105
    im=Image.new("RGB",(w,h),"white"); draw=ImageDraw.Draw(im)
    reg=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",25); bold=ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf",30)
    names=["a","b","c","d","e","f","g"]; vals=[6.630,8.451,9.285,-.702,0,.769,5.856]
    ymin,ymax=-2,10; pw,ph=w-left-right,h-top-bottom
    sy=lambda v:top+(ymax-v)/(ymax-ymin)*ph
    for v in range(-2,11,2):
        y=sy(v); draw.line((left,y,w-right,y),fill="#D9D9D9",width=1); draw.text((35,y-12),f"{v} V",fill="#444",font=reg)
    draw.line((left,sy(0),w-right,sy(0)),fill="#555",width=3)
    pts=[]
    for i,(name,val) in enumerate(zip(names,vals)):
        x=left+i*pw/6; y=sy(val); pts.append((x,y)); draw.text((x-8,h-bottom+22),name,fill="#111",font=bold)
        draw.text((x-30,y-48),f"{val:.3f}",fill="#1B5E20",font=reg)
    draw.line(pts,fill="#1565C0",width=5)
    for x,y in pts: draw.ellipse((x-9,y-9,x+9,y+9),fill="white",outline="#1565C0",width=5)
    draw.text((360,24),"Potential diagram (reference point e = 0 V)",fill="#111",font=bold)
    draw.text((505,h-35),"Circuit node",fill="#111",font=reg)
    im.save(OUTDIR/"实验二_电位图.png")


def build_exp1():
    d=new_doc("实验一 元件伏安特性的测量")
    heading(d,"一、实验目的")
    text(d,"1. 掌握用伏安法测量线性电阻与非线性元件伏安特性的方法，理解电压、电流参考方向与测试接法的关系。")
    text(d,"2. 比较电流表外接法和电压表外接法的测量结果，分析仪表内阻引入的系统误差。")
    text(d,"3. 绘制二极管 IN5401 和发光二极管 D4 的正、反向伏安特性曲线，识别其非线性与单向导电特性。")
    heading(d,"二、实验原理")
    text(d,"线性电阻元件满足欧姆定律 U＝RI，其 U–I 图像为过原点的直线，斜率反映电阻值。非线性元件的 U–I 关系不是直线，电阻随工作点而变；二极管和发光二极管的正、反向特性还具有方向性。")
    text(d,"伏安法中，电流表应串联、电压表应并联。电流表外接时电压表读到被测支路与电流表的总电压，适宜测量小电阻；电压表外接时电流表读到被测元件与电压表支路的总电流，适宜测量大电阻。")
    heading(d,"三、实验电路与仪器")
    figure(d,OUTDIR/"实验1_伏安法接线.png","图1  指导书图4：电流表外接法与电压表外接法（原图）",13.5)
    table(d,["仪器/器材","规格或用途","数量"],[["电路原理实验箱","元件伏安特性的研究单元","1台"],["直流稳压电源","0～24 V","1台"],["直流电流表/万用表","mA、µA量程","各1只"],["直流电压表/万用表","直流电压测量","1只"],["被测元件","R1≈120 Ω、R2≈51 Ω、IN5401、D4 LED","若干"]])
    heading(d,"四、实验步骤")
    text(d,"按图1分别搭建两种伏安法接线。先将电源调至零，再逐点升/降压或升/降流，记录线性电阻的正反向读数；随后测试 IN5401、D4 的正反向特性。D4 测量支路串有实验箱内置1 kΩ限流电阻，反向测试时严格限制电压和电流。")
    heading(d,"五、原始记录与结果分析")
    text(d,"原始数据表请以手写记录为准。下列分析依据提供的电子记录转录，原始照片可粘贴于占位框；附表13～16已按要求绘制为曲线并直接嵌入。")
    placeholder(d,"实验一附表1～12原始数据照片")
    heading(d,"5.1 线性电阻元件",2)
    text(d,"R≈120 Ω 的电压控制/电流控制两组正反向记录中，计算电阻主要落在118.3～119.4 Ω；相对120 Ω标称值的最大偏差约1.4%。R≈51 Ω 的记录主要落在45～55 Ω，除低电压小电流点受分辨率影响较大外，主工作区与标称值相符。正、反向数据近似关于原点对称，说明两只电阻为无方向的线性元件。")
    table(d,["对象","代表性数据","计算/判断"],[["R≈120 Ω","U＝10 V 时 I＝84.1 mA","R＝U/I≈118.9 Ω"],["R≈51 Ω","I＝10 mA 时 U≈0.50～0.51 V","R≈50～51 Ω"],["正反向比较","正、负同幅值下读数符号相反","U–I 近似过原点直线"]])
    heading(d,"5.2 IN5401 二极管",2)
    text(d,"正向记录显示：当电流由1 mA增至10 mA，端电压约从0.550 V升至0.655 V（另一接法为0.549～0.656 V），在约0.55～0.60 V附近出现明显导通区。反向0～20 V范围内电流仅约1～7 µA，远小于正向毫安量级，未出现反向击穿，体现了二极管的单向导电性。")
    heading(d,"5.3 D4 发光二极管：附表13～16曲线",2)
    text(d,"以下四图分别由电子记录中实验一末尾四个表格的数据绘制。正向曲线的横轴为支路电流，纵轴为记录电压；因D4支路串有1 kΩ限流电阻，曲线反映的是带限流支路的外特性。反向电流保持在微安量级。")
    figure(d,OUTDIR/"实验1_附表13_D4正向.png","图2  D4 正向伏安特性（由附表13数据绘制）",11.8)
    figure(d,OUTDIR/"实验1_附表14_D4反向.png","图3  D4 反向伏安特性（由附表14数据绘制）",11.8)
    figure(d,OUTDIR/"实验1_附表15_D4正向.png","图4  D4 正向伏安特性（由附表15数据绘制）",11.8)
    figure(d,OUTDIR/"实验1_附表16_D4反向.png","图5  D4 反向伏安特性（由附表16数据绘制）",11.8)
    text(d,"两组正向数据在1～10 mA内近似呈单调上升，带限流支路的平均斜率约为1.0 V/mA，对应串联限流电阻约1 kΩ；外推截距约为1.8～2.0 V，符合LED的典型导通压降量级。两组反向曲线均显示0～20 V内反向电流不超过2 µA，未发生击穿。")
    heading(d,"六、误差分析")
    text(d,"1. 电流表内阻和电压表有限输入电阻会改变被测支路的等效电阻，是两种接法结果不同的主要系统误差来源。小阻值元件更应注意电流表压降，大阻值元件更应注意电压表分流。")
    text(d,"2. 电阻允差、导线与接触电阻、稳压源带载波动，以及小电流区的末位分辨率，都会使 U/I 在低读数处偏离标称值。")
    text(d,"3. 非线性元件温度敏感，连续测量时结温上升会改变导通电压；反向微安量级数据还易受表计零漂、漏电流和接线清洁度影响。")
    heading(d,"七、思考题与结论")
    text(d,"电流表应与被测元件串联，其内阻应尽可能小；电压表应与被测元件并联，其内阻应尽可能大。开路意味着等效电阻趋于无穷大、电流为零；短路意味着等效电阻趋于零、端电压为零。三端电位器可接作可变电阻、分压器或固定电阻。")
    text(d,"实验结果表明：线性电阻的正反向伏安关系近似为过原点直线，满足欧姆定律；IN5401和D4均呈显著的单向非线性。两种伏安法的差异验证了仪表内阻对测量结果的影响。")
    d.save(OUTDIR/"实验一 元件伏安特性测量实验报告.docx")


def build_exp2():
    d=new_doc("实验二 电路中电位、电压的测定及电路电位图的绘制")
    heading(d,"一、实验目的")
    text(d,"1. 掌握电位、电压（电位差）及参考点之间的关系，理解电位的相对性与电压的参考点无关性。")
    text(d,"2. 测量多节点电路各点电位和支路电压，绘制电位图并验证基尔霍夫电压定律。")
    text(d,"3. 学习采用指零法/电压表法寻找等电位点，比较短接前后电路工作状态。")
    heading(d,"二、实验原理")
    text(d,"选定参考点O后，A点对O点的电压 UAO 称为A点电位 VA；任意两点电压 UAB＝VA－VB。更换参考点只会给所有节点电位同时加上同一常数，不改变任意两点的电压。")
    text(d,"沿任一闭合回路，支路电压的代数和应为零（ΣU＝0）。当两点电位相等时，两点间电压为零；将其短接或断开理想情况下不应改变其余电路的电位与电压。")
    heading(d,"三、实验电路与仪器")
    figure(d,OUTDIR/"实验2_参考点电路.png","图1  指导书图1、图2：以 e 点和 a 点为参考点的电路（原图）",13.5)
    figure(d,OUTDIR/"实验2_等电位电路.png","图2  指导书图3、图4：寻找并判断等电位点的电路（原图）",13.5)
    table(d,["元件","参数/说明"],[["直流电源","Usa＝5 V，Usb＝10 V，二者不共地"],["电阻","R1＝R2＝R7＝220 Ω，R8＝200 Ω"],["电位器","Rw＝500 Ω，可调端用于寻找 e5 等电位点"],["测量仪器","直流电压表、直流电流表、数字万用表"]])
    heading(d,"四、实验步骤")
    text(d,"先以e点为参考点测量a～g各点电位，再以a点为参考点复测；随后测量 Uab、Ubc、Ucd、Ude、Uef、Ufg、Uga。调节Rw的滑动端使e5与e等电位，比较短接前后读数。测量中将D1～D6短接，确保表笔极性与下标顺序一致。")
    heading(d,"五、原始记录与数据验证")
    placeholder(d,"实验二附表1、附表2手工数据照片")
    heading(d,"5.1 参考点改变与电位的相对性",2)
    text(d,"以a点为参考点时，电子记录给出 Va＝0 V、Vb＝1.821 V、Vc＝2.655 V、Vd＝−7.332 V、Ve＝−6.630 V、Vf＝−5.862 V、Vg＝−0.774 V。改以e点为参考点后，对应值为 Va＝6.630 V、Vb＝8.451 V、Vc＝9.285 V、Vd＝−0.702 V、Ve＝0 V、Vf＝0.769 V、Vg＝5.856 V。")
    text(d,"两组电位相差约+6.630 V（例如 1.821＋6.630＝8.451 V，−7.332＋6.630＝−0.702 V），说明改变参考点使各节点电位整体平移，而节点间的相对关系不变。")
    table(d,["节点","以a为参考 (V)","以e为参考 (V)","差值 (V)"],[["a","0.000","6.630","6.630"],["b","1.821","8.451","6.630"],["c","2.655","9.285","6.630"],["d","−7.332","−0.702","6.630"],["e","−6.630","0.000","6.630"],["f","−5.862","0.769","6.631"],["g","−0.774","5.856","6.630"]])
    heading(d,"5.2 等电位点验证",2)
    text(d,"在寻找等电位点后再短接e与e5，记录中各节点电位的最大变化为0.033 V（例如a点0.239 V变为0.272 V，c点−7.840 V变为−7.830 V）。相对于数伏量级节点电位，该变化很小，表明e5已调至与e近似等电位，短接没有明显改变原电路工作状态。")
    heading(d,"5.3 KVL验证",2)
    text(d,"取回路 a→b→c→d→e→f→g→a，按下标顺序对附表2电压代数求和。")
    table(d,["状态","ΣU＝Uab+Ubc+Ucd+Ude+Uef+Ufg+Uga","残差","结论"],[["找到等电位前","5.601+2.327−9.702+2.162+2.325−5.021+2.324","0.016 V","近似为0"],["找到等电位后","5.575+2.507−10.014+2.175+2.388−5.024+2.393","0.000 V","满足KVL"],["等电位点短接后","5.594+2.515−10.015+2.181+2.396−5.032+2.361","0.000 V","满足KVL"]])
    text(d,"三种状态下闭合回路的电压代数和均接近零；后两组在给定有效数字下恰为零，验证了基尔霍夫电压定律。")
    heading(d,"六、电位图绘制说明")
    figure(d,OUTDIR/"实验二_电位图.png","图3  以 e 点为参考点的实测电位图",12.5)
    text(d,"以e为零电位基准，可按节点顺序标注：a=6.630 V、b=8.451 V、c=9.285 V、d=−0.702 V、e=0 V、f=0.769 V、g=5.856 V。绘图时以水平零线表示e点，其他点按正负电位在零线上下标出高度，再按实际拓扑连接相邻节点；任一支路的竖向高度差即为该支路电压。")
    heading(d,"七、误差分析")
    text(d,"1. 电压表有限输入电阻会使高阻支路产生分流；表笔接触电阻、插孔氧化和电源纹波会带来附加误差。")
    text(d,"2. 电位读数的正负号依赖参考点和表笔极性。若没有按 UAB 的下标顺序接表笔，数值符号会错误，从而使KVL代数和失真。")
    text(d,"3. 电位器滑动端具有接触电阻，指零判断受仪表分辨率影响，因此等电位点只能达到近似；记录中短接前后的0.033 V最大差异反映了这一限制。")
    heading(d,"八、思考题与结论")
    text(d,"参考点是人为选定的零电位基准；改变参考点会改变全部节点电位的数值，但不会改变任意两点的电压。等电位点是电位相同的两点，理想短接/断开不会改变其他节点的电位和各支路电压，因为两点间无驱动电压、无电流。")
    text(d,"本实验实测表明：参考点由a改为e后各节点电位统一平移约6.630 V；闭合回路电压代数和的最大残差仅0.016 V；等电位点短接前后节点变化很小。实验结果与电位相对性及KVL一致。")
    d.save(OUTDIR/"实验二 电位电压测定与电位图实验报告.docx")


if __name__ == "__main__":
    render_crops(); make_charts(); build_exp1(); build_exp2()
    print("reports created")
