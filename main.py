# Jan.19.2018
# Atlanta Regional Commission.
# Jueun Kim

from os.path import join, dirname
import pandas as pd
import bokeh.models.tools as bmt
from bokeh.models import ColumnDataSource,LabelSet,Select,CategoricalColorMapper, Div
from bokeh.layouts import row, widgetbox
from bokeh.palettes import Spectral5
from bokeh.plotting import curdoc, figure
from collections import OrderedDict


df = pd.read_csv(join(dirname(__file__),'data/sample_D.csv'))
SIZES = list(range(6, 22, 3))
COLORS = Spectral5

desc = Div(text=open(join(dirname(__file__), "description.html")).read(), width=800)
new = df[['ProjectID','ProjectType','Jurisdiction','ProjectDescription','Cost']].copy()

del df['ProjectID']
del df['ProjectType']
del df['Jurisdiction']
del df['ProjectDescription']
del df['Cost']

columns = sorted(df.columns)
discrete = [x for x in columns if df[x].dtype == object]
continuous = [x for x in columns if x not in discrete]
quantileable = [x for x in continuous if len(df[x].unique()) > 20]


# Set up widgets
x = Select(title='X-Axis', value='Reliability', options=columns)
y = Select(title='Y-Axis', value='Multimodalism', options=columns)
size = Select(title='Size', value='Reliability', options=['None'] + quantileable)
color = Select(title='Color', value='Reliability', options=['None'] + quantileable)
# p_type = Select(title='Project Type', value ='None',options = sorted(project_types.keys()))

def update(attr, old, new):
    layout.children[1] = create_figure()


def create_figure():
    # # Create Column Data Source that will be used by the plot
    source = ColumnDataSource(data=dict(x = [], y=[],PID = [], Jurisdiction=[], projectT=[], projectD=[], Cost=[]))
    hover = bmt.HoverTool(tooltips=[
        ("Project ID", "@PID"),
        ("Jurisdiction", "@Jurisdiction"),
        ("Project Type", "@projectT"),
        ("Project Description", "@projectD"),
        ("Cost in Millions", "@Cost"),
    ])
    TOOLS = [bmt.BoxZoomTool(), bmt.PanTool(), hover, bmt.ResetTool(), bmt.SaveTool(), bmt.WheelZoomTool()]

    xs = df[x.value].values
    ys = df[y.value].values
    x_title = x.value.title()
    y_title = y.value.title()

    kw = dict()
    if x.value in discrete:
        kw['x_range'] = sorted(set(xs))
    if y.value in discrete:
        kw['y_range'] = sorted(set(ys))
    kw['title'] = "%s vs %s" % (x_title, y_title)

    # 'pan,wheel_zoom,box_zoom,reset,save,hover'
    # plot = figure(plot_height=600, plot_width=800, tools=" ", **kw)
    # plot = figure(plot_height=600, plot_width=800, tools='')
    plot = figure(plot_height=600, plot_width=800, tools=TOOLS, **kw)
    plot.xaxis.axis_label = x_title
    plot.yaxis.axis_label = y_title

    if x.value in discrete:
        plot.xaxis.major_label_orientation = pd.np.pi / 4

    sz = 13
    if size.value != 'None':
        groups = pd.qcut(df[size.value].values, len(SIZES), duplicates='drop')
        sz = [SIZES[xx] for xx in groups.codes]

    c = "#31AADE"
    if color.value != 'None':
        groups = pd.qcut(df[color.value].values, len(COLORS),duplicates='drop')
        c = [COLORS[xx] for xx in groups.codes]

    source.data = dict(
        Jurisdiction = new["Jurisdiction"],
        projectD=new["ProjectDescription"],
        projectT=new["ProjectType"],
        PID = new["ProjectID"],
        Cost = new["Cost"]
    )

    plot.circle(x=xs, y=ys, source = source,color=c, size=sz, line_color="white", alpha=0.6, hover_color='white', 
        hover_alpha=0.5,
    )


    return plot


controls = [x, y, size, color]
for control in controls:
    control.on_change('value', update)

inputs = widgetbox([x, y, color, size], width=240)
layout = row(inputs, create_figure())

curdoc().add_root(desc)

curdoc().add_root(layout)
curdoc().title = "ARC project evaluation"
