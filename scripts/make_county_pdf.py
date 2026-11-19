# Oklahoma 77-county PDF, modeled on Nebraska_93_County_Democratic_Registration_and_Vote_Change.pdf (landscape letter, Carlito/Caladea,
# navy header repeated on each page, legend highlights, statewide total row, footer "Page X of Y"). Data: verified pass A county file.
import pandas as pd, json
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
FD='/usr/share/fonts/truetype/sand-box/google/'
for n,f in [('Carlito','Carlito/Carlito-Regular.ttf'),('Carlito-Bold','Carlito/Carlito-Bold.ttf'),('Caladea','Caladea/Caladea-Regular.ttf'),('Caladea-Italic','Caladea/Caladea-Italic.ttf'),('Caladea-Bold','Caladea/Caladea-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(n,FD+f))
V='/workspace/oklahoma/verification/'; RAW='/workspace/oklahoma/raw/'; OUT='/workspace/oklahoma/pdf/Oklahoma_77_County_Democratic_Registration_and_Vote_Change.pdf'
o=pd.read_csv(V+'passA_counties.csv',index_col=0)
o['share26']=o.DREG26/o.TREG26
o=o.sort_values('share26',ascending=False)
nm=lambda c: c.title().replace('Mcc','McC').replace('Mci','McI').replace('Leflore','Le Flore')
ball=json.load(open('/workspace/oklahoma/repo/OK_results_summary.json'))['ballots_statewide']
NAVY=colors.HexColor('#1F2A44'); BLUE=colors.HexColor('#DCE9F7'); ORANGE=colors.HexColor('#FBE3D6')
def i(x): return f"{int(x):,}"
def si(x): x=int(x); return f"+{x:,}" if x>0 else (f"-{abs(x):,}" if x<0 else "0")
def p1(x): return f"{x:.1f}%"
def sp(x): s=f"{x:+.1f}%"; return s
def spt(x): return f"{x:+.2f}"
rose=[c for c in o.index if o.loc[c,'DREG26']>o.loc[c,'DREG22']]; fell=[c for c in o.index if o.loc[c,'D26']<o.loc[c,'D22']]
tot={k:int(o[k].sum()) for k in ['DREG22','DREG26','TREG22','TREG26','D22','D26','T22','T26']}
H=ParagraphStyle('h',fontName='Carlito-Bold',fontSize=8,leading=9,textColor=colors.white,alignment=1)
T=ParagraphStyle('t',fontName='Carlito-Bold',fontSize=14,leading=17)
I=ParagraphStyle('i',fontName='Caladea-Italic',fontSize=7.6,leading=9.2)
L=ParagraphStyle('l',fontName='Caladea',fontSize=7.6,leading=9)
LB=ParagraphStyle('lb',fontName='Carlito-Bold',fontSize=8.5,leading=10)
SORT=("Sorted by 2026 Democratic share of registration (Democratic registered voters ÷ all registered voters, Nov 1, 2026), highest first. "
      f"{nm(o.index[0])} leads by share; Oklahoma County leads by raw Democratic registration.")
NOTE=("*2026 figures are marked unofficial by project rule (Oklahoma State Election Board County Level Results export for the Nov 3, 2026 general election, "
      "data last updated 11/06/2026, retrieved 19 Nov 2026; the Board's results site labels them \"Official Results\"). 2022 votes: Board official results. "
      "Registration: Board report vr2420, Current Registration Statistics by County, as of Nov 1, 2022 and Nov 1, 2026 (election time). "
      "Votes are votes for the Democratic governor candidate, not a count of registered Democrats who voted.")
BALL=("<b>Total Gov Votes</b> = total governor votes, all candidates. <b>OK does not publish county ballots cast</b>, so this column stands in for Nebraska's "
      f"Total Ballots; no ballot counts were estimated. Statewide ballots cast from the Board's published statewide turnout %: {ball['22']['rounded']:,} (2022) and "
      f"{ball['26']['rounded']:,}* (2026).")
def footer(c,doc):
    c.saveState(); c.setFont('Caladea-Italic',8); c.drawString(0.45*72,0.35*72,'*2026 figures marked unofficial (project rule); Board site labels them "Official Results"')
    c.drawRightString(11*72-0.45*72,0.35*72,f"Page {doc.page} of {{NP}}"); c.restoreState()
def build(np_):
    doc=BaseDocTemplate(OUT,pagesize=landscape(letter),leftMargin=0.45*72,rightMargin=0.45*72,topMargin=0.4*72,bottomMargin=0.6*72,
        title='Oklahoma 77 Counties — Democratic Registration, Democratic Governor Votes and Total Governor Votes, 2022 vs 2026*',author='Oklahoma Election Analysis')
    def ft(c,d):
        c.saveState(); c.setFont('Caladea-Italic',8); c.drawString(0.45*72,0.35*72,'*2026 figures marked unofficial (project rule); Board site labels them "Official Results"')
        c.drawRightString(11*72-0.45*72,0.35*72,f"Page {d.page} of {np_}"); c.restoreState()
    doc.addPageTemplates([PageTemplate(frames=[Frame(doc.leftMargin,doc.bottomMargin,doc.width,doc.height,id='f',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=ft)])
    st=[]
    # ---------- Part 1 ----------
    st.append(Paragraph('Oklahoma 77 Counties — Democratic Registration, Democratic Governor Votes and Total Governor Votes, 2022 vs 2026*',T))
    st.append(Paragraph(SORT,I)); st.append(Spacer(1,6)); st.append(Paragraph(NOTE,I)); st.append(Paragraph(BALL,I)); st.append(Spacer(1,5))
    lg=Table([[Paragraph('Legend:',LB),Paragraph(f"Democratic registration rose ({', '.join(nm(c) for c in rose)})",L),Paragraph(f"Democratic governor votes fell ({len(fell)} counties)",L)]],colWidths=[60,250,250])
    lg.setStyle(TableStyle([('BACKGROUND',(1,0),(1,0),BLUE),('BACKGROUND',(2,0),(2,0),ORANGE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),2),('TOPPADDING',(0,0),(-1,-1),1),('BOTTOMPADDING',(0,0),(-1,-1),2)]))
    st.append(lg); st.append(Spacer(1,3))
    hdr=['County','Dem Reg Share 2026 %','Dem Reg 2022 (Nov 1)','Dem Reg 2026 (Nov 1)','Reg Change #','Reg Change %','Dem Gov Votes 2022','Dem Gov Votes 2026*','Vote Change #','Vote Change % (on 2022 base)',
         'Total Gov Votes 2022 †','Total Gov Votes 2026* †','Gov Votes Change #','Gov Votes Change %']
    rows=[[Paragraph(h,H) for h in hdr]]
    def r1(name,x):
        return [name,p1(100*x['DREG26']/x['TREG26']),i(x['DREG22']),i(x['DREG26']),si(x['DREG26']-x['DREG22']),sp(100*(x['DREG26']/x['DREG22']-1)),
                i(x['D22']),i(x['D26']),si(x['D26']-x['D22']),sp(100*(x['D26']/x['D22']-1)),i(x['T22']),i(x['T26']),si(x['T26']-x['T22']),sp(100*(x['T26']/x['T22']-1))]
    for c in o.index: rows.append(r1(nm(c),o.loc[c]))
    rows.append(r1('Statewide total',tot))
    rest=doc.width-82; wts=[1,1.1,1.1,1,1,1,1.05,1,1.15,1,1.05,1,1]; cw=[82]+[rest*w/sum(wts) for w in wts]
    t=Table(rows,colWidths=cw,repeatRows=1,rowHeights=[50]+[12.2]*(len(rows)-1))
    sty=[('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,0),'MIDDLE'),('TOPPADDING',(0,0),(-1,0),2),('BOTTOMPADDING',(0,0),(-1,0),2),('FONT',(0,1),(-1,-1),'Caladea',8),('ALIGN',(1,1),(-1,-1),'RIGHT'),
         ('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#9AA3B2')),('TOPPADDING',(0,1),(-1,-1),1),('BOTTOMPADDING',(0,1),(-1,-1),2),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3),
         ('FONT',(0,-1),(-1,-1),'Caladea-Bold',8),('LINEABOVE',(0,-1),(-1,-1),1.2,NAVY)]
    for k,c in enumerate(o.index,1):
        if c in rose: sty.append(('BACKGROUND',(0,k),(-1,k),BLUE))
        elif c in fell: sty.append(('BACKGROUND',(0,k),(-1,k),ORANGE))
    t.setStyle(TableStyle(sty)); st.append(t)
    st.append(Spacer(1,4)); st.append(Paragraph("† Total governor votes (OK does not publish county ballots cast).",I))
    st.append(PageBreak())
    # ---------- Part 2 ----------
    st.append(Paragraph('Democratic Governor Votes as a Share of Total Governor Votes, and Democratic Share of Registration, 2022 vs 2026*',T))
    st.append(Paragraph(SORT,I)); st.append(Spacer(1,6)); st.append(Paragraph(NOTE,I))
    st.append(Paragraph("Share of governor votes = Democratic governor votes ÷ total governor votes, all candidates (OK does not publish county ballots cast). Share of registration = Democratic registered voters ÷ all registered voters. Change (pts) = 2026 share minus 2022 share, in percentage points.",I))
    st.append(Spacer(1,4))
    h2=['County','Dem Share of Gov Votes 2022 % †','Dem Share of Gov Votes 2026* % †','Change (pts)','Dem Share of Registration 2022 %','Total Registered 2022 (Nov 1)','Dem Share of Registration 2026 %','Total Registered 2026 (Nov 1)']
    rows=[[Paragraph(h,H) for h in h2]]
    def r2(name,x):
        a=100*x['D22']/x['T22']; b=100*x['D26']/x['T26']
        return [name,p1(a),p1(b),spt(b-a),p1(100*x['DREG22']/x['TREG22']),i(x['TREG22']),p1(100*x['DREG26']/x['TREG26']),i(x['TREG26'])]
    for c in o.index: rows.append(r2(nm(c),o.loc[c]))
    rows.append(r2('Statewide total',tot))
    t=Table(rows,colWidths=[110]+[75]*7,repeatRows=1,rowHeights=[40]+[13.2]*(len(rows)-1),hAlign='CENTER')
    sty2=[s for s in sty if s[0]!='BACKGROUND' or s[1]==(0,0)]
    for k,c in enumerate(o.index,1):
        if c in rose: sty2.append(('BACKGROUND',(0,k),(-1,k),BLUE))
        elif c in fell: sty2.append(('BACKGROUND',(0,k),(-1,k),ORANGE))
    t.setStyle(TableStyle(sty2)); st.append(t)
    st.append(Spacer(1,4)); st.append(Paragraph("† Total governor votes (OK does not publish county ballots cast).",I))
    doc.build(st); return doc.page
n1=build('?'); n2=build(n1); print('pages',n1,n2)
