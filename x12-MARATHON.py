import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
pio.renderers.default = 'png'   # dinamic format:'browser'|static format: 'png'
pd.options.display.float_format='{:20.2f}'.format
plt.style.use('dark_background')
pd.set_option('display.max_columns',None)

# READING ________________________________
df=pd.read_csv('x12-marathon.csv')

df.info()

# CLEANING ________________________________

df.isna().sum()[df.isna().sum()>0].sort_values(ascending=False)

df=df.loc[df['Athlete country']=='IND']

df['Event distance/length'].nunique()

df['Event distance/length'].value_counts().reset_index().head()

df=df.loc[df['Event distance/length'].isin(['50km','12h','100km','24h'])]

df['Athlete club'].value_counts().head()

len(df)

df=df.dropna(subset=['Athlete year of birth'])
len(df)

df.isnull().sum()[df.isnull().sum()>0].sort_values(ascending=False)

df['Athlete year of birth'].value_counts().head()

df['Athlete year of birth']=df['Athlete year of birth'].astype('int')
df.info()

df['Athlete age']=df['Year of event']-df['Athlete year of birth']

df['Athlete performance']=df['Athlete performance'].str.split(' ').str.get(0)

df=df.drop_duplicates()

df=df.reset_index(drop=True)

df['Athlete average speed']=df['Athlete average speed'].astype(float)

df=df.loc[df['Athlete average speed']<20]

df=df.drop(['Athlete club','Athlete year of birth'],axis=1)

# ANALYSIS ________________________________
#   graph-heatmap and pairplot
plt.figure(figsize=(15,5))
sns.heatmap(df.corr(numeric_only=True).dropna().round(2)\
            ,annot=True,cmap='Blues') # other colors: coolwarm,viridis,GnYlBu,magma
sns.pairplot(df,kind='scatter',plot_kws={'alpha':.5}\
             ,hue='Athlete gender')

top_events=df['Event name'].value_counts().head()
#   graph-bar vertical 
fig=px.bar(x=top_events.index,y=top_events.values,title='XXX'
           ,text_auto=True,color=top_events.values,color_continuous_scale='purples',orientation='v') #OTHER COLORS: blues
fig.update_layout(xaxis_title='x',yaxis_title='y'
                  ,hovermode='x unified',template='plotly_dark',width=800,height=400)

#   graph-bar horizontal
fig=px.bar(x=top_events.values,y=top_events.index,title='xxx'
           ,text_auto=True,color_discrete_sequence=['maroon'],orientation='h')
fig.update_layout(xaxis_title='x',yaxis_title='y'
                  ,hovermode='x unified',template='plotly_dark',width=800,height=300)

#   graph-bar mixed distribution 
fig=px.histogram(df, x='Event distance/length',color='Athlete gender',title='xxx'
                 ,text_auto=True,color_discrete_map={'M':'maroon','F':'white'})
fig.update_layout(xaxis_title='x',yaxis_title='y'
                  ,hovermode='x unified',template='plotly_dark',width=600,height=400)

#   graph-line
#       people_by_year:pby
pby=df['Year of event'].value_counts().sort_index()
fig=px.line(x=pby.index,y=pby.values,title='x',markers=True)  #,text=pby.values
fig.update_layout(xaxis_title='year',yaxis_title='count of people'
                  ,template='plotly_dark',hovermode='x unified',width=800,height=400)
fig.update_traces(line=dict(width=1,color='lightgreen'),marker=dict(size=5)) #,textfont_size=11,textposition='top center'

#   graph-line combine
#       people by year by gender:pbyg
pbyg=df.groupby(['Year of event','Athlete gender']).size().reset_index(name='count')
fig=px.line(pbyg,x='Year of event', y='count',title='x'
            ,color='Athlete gender',color_discrete_map={'M':'lightgreen','F':'violet'}, markers=True)
fig.update_layout(xaxis_title='year',yaxis_title='count',template='plotly_dark',hovermode='x unified'
                  ,width=800,height=400)
fig.update_traces(line=dict(width=1))

#       resume table by cross twho columns
race_gender=pd.crosstab(index=df['Event distance/length'],columns=df['Athlete gender'])

#   graph-histogram + box
fig=px.histogram(df,x='Athlete age',title='DIST-AGE'
                 ,color_discrete_sequence=['lightgreen'],marginal='box') #color:navy
fig.update_layout(xaxis_title='athlete age',yaxis_title='count of people'
                  ,template='plotly_dark',width=800,height=400)

#   graph-histogram + box
fig=px.histogram(df, x='Athlete average speed',title='DIST-SPEED'
                 ,color_discrete_sequence=['steelblue'],marginal='box')
fig.update_layout(xaxis_title='speed',yaxis_title='count of people'
                  ,template='plotly_dark',width=800,height=400)

#   graph-box mixed
fig=px.box(df,x='Athlete average speed',y='Athlete gender',title='GENDER-SPEED'
           ,color='Athlete gender')
fig.update_layout(xaxis_title='speed',yaxis_title='gender',template='plotly_dark',width=800,height=300)

#   graph-box mixed
fig=px.box(df,x='Athlete age',y='Athlete gender',title='GENDER & AGE'
           ,color='Athlete gender',color_discrete_map={'M':'lightgreen','F':'violet'})
fig.update_layout(xaxis_title='age',yaxis_title='gender'
                  ,template='plotly_dark',width=800,height=300)

#__ CATEGORY AGRUPATION AND ANALYTICS
# age vs speed:avs
avs=df.groupby(['Athlete age category'])['Athlete average speed'].agg(['mean','count'])\
    .sort_values(by='mean',ascending=False).query('count>20').reset_index()

#   graph-double axis
fig=make_subplots(specs=[[{'secondary_y':True}]])
fig.add_trace(go.Scatter(x=avs['Athlete age category'],y=avs['mean']
                         ,name='mean',mode='lines+markers',line=dict(color='lightgreen',width=1))
                         ,secondary_y=False)
fig.add_trace(go.Bar(x=avs['Athlete age category'],y=avs['count']
                         ,name='count',marker_color='steelblue',opacity=.5)
                         ,secondary_y=True)
fig.update_layout(title_text='category/speed',xaxis_title='category'
                  ,template='plotly_dark',hovermode='x unified',width=800,height=400)
fig.update_yaxes(title_text='mean',secondary_y=False)
fig.update_yaxes(title_text='count',secondary_y=True)

#__ agrupation stats
# distance per gender= dpg
dpg=df.groupby(['Event distance/length','Athlete gender'])['Athlete average speed']\
    .agg(['mean','count']).sort_values(by='mean',ascending=False).reset_index()

# =============================================================================
# #   graph-double axis
# fig=make_subplots(specs=[[{'secondary_y':True}]])
# fig.add_trace(go.Scatter(x=dpg['Event distance/length'],y=dpg['count']
#                          ,name='mean',line=dict(color='yellow'))
#               ,secondary_y=False)
# fig.add_trace(go.Bar(x=dpg['Event distance/length'],y=dpg['mean']
#                      ,name='count',marker_color='steelblue',opacity=.3)
#               ,secondary_y=True)
# fig.update_layout(title_text='distance/speed',xaxis_title='event distance'
#                   ,template='plotly_dark',hovermode='x unified')
# fig.update_yaxes(title_text='mean',secondary_y=False)
# fig.update_yaxes(title_text='count',secondary_y=True)
# #       shouldnt graphic dataframes with double inlet from any axis(x or y)
# #       if break the graph 'visually' cant give coherence
# =============================================================================

#   graph-bar vertical mixed-type2
fig=px.bar(dpg,x='mean',y='Event distance/length',title='distance by gender'
           ,color='Athlete gender',text_auto=True,barmode='group',orientation='h')
fig.update_layout(xaxis_title='mean',yaxis_title='lenght of race'
                  ,hovermode='x unified',template='plotly_dark')
fig.show()
#       barmode= 'stack'(superpuestos),'group'(paralelos),'overlay'(superpuestos)|for distribution in cols

#__ agrupation stats
distance=df.groupby(['Event distance/length','Athlete gender'])\
    .agg({'Athlete gender':'count','Athlete average speed':['mean','count']})
distance
#   graph-violin partition
plt.figure(figsize=(10,5))
sns.violinplot(data=df,x='Event distance/length',y='Athlete average speed'
               ,hue='Athlete gender',split=True,inner='quartile')\
    .set(title='x',xlabel='x')
plt.tight_layout()

# graph-box
fig=px.box(df,x='Event distance/length',y='Athlete average speed',title='GENDER & AGE'
           ,color='Athlete gender')
fig.update_layout(xaxis_title='age',yaxis_title='gender'
                  ,template='plotly_dark',width=800,height=300)

df.info()
# clean data-analytic date transfomation (from object to date)
df['Event dates']=pd.to_datetime(df['Event dates'],errors='coerce')

df['Athlete performance'] = pd.to_timedelta(df['Athlete performance'], errors='coerce')

#   graph-box
filtered_df=df[df['Event distance/length'].isin(['50km','100km'])]
filtered_df['Running hours']=filtered_df['Athlete performance'].dt.hour

fig=px.box(filtered_df,x='Event distance/length',y='Running hours',title='x'
           ,color='Athlete gender')
fig.update_layout(xaxis_title='distances',yaxis_title='performance'
                  ,template='plotly_dark')

#   graph-line
df_agrupado= filtered_df.groupby(filtered_df['Running hours'])\
    ['Athlete average speed'].mean().reset_index()
fig=px.line(df_agrupado,x='Athlete performance',y='Athlete average speed',
              title='Time vs Speed',markers=True,)
fig.update_layout(template='plotly_dark',hovermode='x unified')
fig.show()

#   New data base
df['Run min']=df['Athlete performance'].dt.minute/60
df['Run hour']=df['Athlete performance'].dt.hour

df['Run tot']=df['Run hour']+df['Run min']

#   events by hours: ebh
ebh=df.groupby('Event name')['Run tot']\
    .agg(['mean','count','max','min']).query('count>20').reset_index()

#   graph-line
#       mean of finish-ebh_mean
ebh_mean=ebh.sort_values(by='mean',ascending=False)

fig=px.line(x=ebh_mean['Event name'].head(),y=ebh_mean['mean'].head()
            ,title='event name-mean',markers=True)
fig.update_layout(template='plotly_dark',hovermode='x unified')
fig.show()

#   group and stats
#       fastest to finish-ebh_min
ebh_min=ebh.sort_values(by='min',ascending=True)

fig=px.bar(ebh_min.head(),x='Event name',y='min'
           ,text_auto=True,title='ebh_min')
fig.update_layout(template='plotly_dark')
fig.show()

#   slowest to finish-ebh_max
ebh_max=ebh.sort_values(by='max',ascending=False)

fig=px.bar(ebh_max.head(),x='max',y='Event name'
           ,color='Athlete gender',text_auto=True,barmode='stack',orientation='h') #barmode= 'stack'(superpuestos),'group'(paralelos),'overlay'(superpuestos)
fig.update_layout(template='plotly_dark')
fig.show()

#   season in function of month
df['season']=df['Event dates'].dt.month\
    .apply(lambda x: 'winter'if x>11 else 'fall'if x>8 else 'summer' 
          if x>3 else 'spring'if x>2 else 'winter')

# season count:sc
sc=df.season.value_counts()

#   graph-pie
fig=px.pie(names=sc.index,values=sc.values,title='people by season'
           ,hole=.5)
fig.update_layout(template='plotly_dark')
fig.update_traces(textposition='outside',textinfo='percent+label')
fig.show()

df.info()
#   group-stats
#       season by gender:sbg
sbg=df.groupby(['season','Athlete gender'])\
    .agg({'Athlete gender':'count','Athlete average speed':['mean','max']})

#       season by speed:sbs
sbs=df.groupby('season')['Athlete average speed']\
    .agg(['mean','count']).sort_values(by='mean',ascending=False).reset_index()

#   graph-line
fig=px.line(sbs,x='season',y='mean',title='speeds by season'
            ,markers=True)
fig.update_layout(template='plotly_dark',hovermode='x unified')
fig.update_traces(line=dict(color='yellow'))
fig.show()




















