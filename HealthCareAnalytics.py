import streamlit as st
import pandas as pd
import sqldf
import seaborn as sns
import matplotlib.pyplot as plt
import base64
import plotly.express as px

@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    body {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return


# Security
#passlib,hashlib,bcrypt,scrypt
import hashlib
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False
# DB Management
import sqlite3 
conn = sqlite3.connect('HealthCareAnalytics.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT count(*) FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchone()[0]
	return data


def user_exists(username):
	c.execute('SELECT count(*) FROM userstable WHERE username =?',(username,))
	data = c.fetchone()[0]
	return data

def load_data(FileName):
    data = pd.read_csv(FileName)
    return data


st.title("Welcome to BHCI Exploration!")

#menu = ["Login","SignUp"]
#choice = st.sidebar.selectbox("Menu",menu)
#if choice == "Login":
st.set_option('deprecation.showPyplotGlobalUse', False)
#Load DataFrame
df=pd.DataFrame()

df=load_data('BCHI-dataset.csv')
df.dropna(inplace=True)
df.rename(columns={'Indicator Category':'indic_cat','Race/Ethnicity':'Race'}, inplace=True)
def get_bar_plots(df_per_indicator,indicator_name,indic_cat,x,color):
	
	sorty=sorted(df_per_indicator["Value"],reverse=True)
	if(color==""):
		fig = px.bar(df_per_indicator, x=x, y=sorty,title=indicator_name + " per countries")
	else:
		fig = px.bar(df_per_indicator, x=x, y=sorty,title=indicator_name + " per countries",color=color,barmode="group")
	fig.update_layout(
    autosize=False,
    width=900,
    height=500,)
	return fig
def get_line_plots(df_per_indicator,indicator_name,indic_cat):
	fig = px.line(df_per_indicator, x='Year', y='Value',title=indicator_name + " per year")
	fig.update_layout(
    autosize=False,
    width=900,
    height=500,)
	return fig

def main():
	"""Simple Login App"""

	menu = ["Home","Login","SignUp"]
	choice = st.sidebar.selectbox("Menu",menu)

	if choice == "Home":
			st.markdown("""<p style="text-align: justify;"><span style="font-size: 18px;">This dataset illustrates health status of 26 of the nation&rsquo;s largest and most urban cities as captured by 34 health <span style="white-space:pre;">&nbsp;</span>(and six demographics-related) indicators. These indicators represent some of the leading causes of morbidity and mortality in the United States <span style="white-space:pre;">&nbsp;</span>and leading priorities of national, state, and local health agencies. Public health data were captured in nine overarching categories: HIV/AIDS, cancer, nutrition/physical activity/obesity, food safety, infectious disease, maternal and child health, tobacco, injury/violence, and behavioral health/substance abuse..</span></p>
<p style="text-align: justify;"><em><strong><span style="font-size: 18px;">Source: https://bchi.bigcitieshealth.org/indicators/1827/searches/34444</span></strong></em></p>""",unsafe_allow_html=True)

	elif choice == "Login":
		username = st.sidebar.text_input("User Name")
		password = st.sidebar.text_input("Password",type='password')
		if st.sidebar.checkbox("Login",key='0'):
		
			# if password == '12345':
			create_usertable()
			hashed_pswd = make_hashes(password)

			result = login_user(username,check_hashes(password,hashed_pswd))
			if result:
				#if result>0:
				lst_indic_cat = df["indic_cat"].unique()
				indic_cat = st.sidebar.selectbox("Indicator Category", lst_indic_cat)
				dash=st.sidebar.radio(label="View Dashboard by", options=["Country", "Year & Country","Sex & Country"])
				query="SELECT Distinct(Indicator) from df where indic_cat like '{}'".format(indic_cat)
				indicators=sqldf.run(query)
				indicators=indicators['Indicator'].values.tolist()
				num_of_indicators=len(indicators)
				num_of_div=int(num_of_indicators/2)
				if dash=="Country":
					indx=0
					st.subheader("Dashboard showing different Indicators of "  + indic_cat + " Category By Country")
					if num_of_indicators == 1:
						c_plot0,c_plot1=st.beta_columns(2)
						query="SELECT Value,Place from df where Indicator like '{}'".format(indicators[indx]) + " group by Place"
						df_per_indicator=sqldf.run(query)
						fig=get_bar_plots(df_per_indicator,indicators[indx],indic_cat,'Place',"")
						c_plot0.plotly_chart(fig,use_container_width=True)
					else:
						if num_of_indicators > 1:
							for div in range(num_of_div):
								c_plot1,c_plot2=st.beta_columns(2)
								c_plots=[c_plot1,c_plot2]
								for i in range(2):
									query="SELECT Sum(Value) Value,Place from df where Indicator like '{}'".format(indicators[indx]) + " group by Place"
									df_per_indicator=sqldf.run(query)
									fig=get_bar_plots(df_per_indicator,indicators[indx],indic_cat,'Place',"")
									c_plots[i].plotly_chart(fig,use_container_width=True)
									indx=indx+1
							if  num_of_indicators%2 > 0:
								c_plot3,c_plot4=st.beta_columns(2)
								query="SELECT Value,Place from df where Indicator like '{}'".format(indicators[indx]) + " group by Place"
								df_per_indicator=sqldf.run(query)
								fig=get_bar_plots(df_per_indicator,indicators[indx],indic_cat,'Place',"")
								c_plot3.plotly_chart(fig,use_container_width=True)
				else:
					if dash=="Year & Country":
						lst_countries=df["Place"].unique()
						place=st.sidebar.selectbox("Select Country to Filter on", lst_countries)
						indx=0
						st.subheader("Dashboard showing different Indicators of "  + indic_cat + " Category By Year")
						if num_of_indicators == 1:
							c_plot0,c_plot1=st.beta_columns(2)
							query="SELECT Sum(Value) Value,Year from df where Indicator like '{}'".format(indicators[indx]) + " and Place like '{}'".format(place) + " group by Year"
							df_per_indicator=sqldf.run(query)
							fig=get_line_plots(df_per_indicator,indicators[indx],indic_cat)
							c_plot0.plotly_chart(fig,use_container_width=True)
						else:
							if num_of_indicators > 1:
								for div in range(num_of_div):
									c_plot1,c_plot2=st.beta_columns(2)
									c_plots=[c_plot1,c_plot2]
									for i in range(2):
										query="SELECT Sum(Value) Value,Year from df where Indicator like '{}'".format(indicators[indx]) + " and Place like '{}'".format(place) + " group by Year"
										df_per_indicator=sqldf.run(query)
										fig=get_line_plots(df_per_indicator,indicators[indx],indic_cat)
										c_plots[i].plotly_chart(fig,use_container_width=True)
										indx=indx+1
								if  num_of_indicators%2 > 0:
									c_plot3,c_plot4=st.beta_columns(2)
									query="SELECT Sum(Value) Value,Year from df where Indicator like '{}'".format(indicators[indx]) + " and Place like '{}'".format(place) + " group by Year"
									df_per_indicator=sqldf.run(query)
									fig=get_line_plots(df_per_indicator,indicators[indx],indic_cat)
									c_plot3.plotly_chart(fig,use_container_width=True)
					else:
						lst_countries=df["Place"].unique()
						place=st.sidebar.selectbox("Select Country to Filter on", lst_countries)
						indx=0
						st.subheader("Dashboard showing different Indicators of "  + indic_cat + " Category By Sex")
						if num_of_indicators == 1:
							c_plot0,c_plot1=st.beta_columns(2)
							query="SELECT Sum(Value) Value,Sex,Race from df where Indicator like '{}'".format(indicators[indx]) + " and Place like '{}'".format(place) + " group by Sex,Race"
							df_per_indicator=sqldf.run(query)
							fig=get_bar_plots(df_per_indicator,indicators[indx],indic_cat,'Sex','Race')
							c_plot0.plotly_chart(fig,use_container_width=True)
						else:
							if num_of_indicators > 1:
								for div in range(num_of_div):
									c_plot1,c_plot2=st.beta_columns(2)
									c_plots=[c_plot1,c_plot2]
									for i in range(2):
										query="SELECT Sum(Value) Value,Sex,Race from df where Indicator like '{}'".format(indicators[indx]) + " and Place like '{}'".format(place) + " group by Sex,Race"
										df_per_indicator=sqldf.run(query)
										fig=get_bar_plots(df_per_indicator,indicators[indx],indic_cat,'Sex','Race')
										c_plots[i].plotly_chart(fig,use_container_width=True)
										indx=indx+1
								if  num_of_indicators%2 > 0:
									c_plot3,c_plot4=st.beta_columns(2)
									query="SELECT Sum(Value) Value,Sex,Race from df where Indicator like '{}'".format(indicators[indx]) + " and Place like '{}'".format(place) + " group by Sex,Race"
									df_per_indicator=sqldf.run(query)
									fig=get_bar_plots(df_per_indicator,indicators[indx],indic_cat,'Sex','Race')
									c_plot3.plotly_chart(fig,use_container_width=True)
				if st.sidebar.checkbox("Some Insights",False,key='1'):
					my_expander = st.beta_expander("Expand to View", expanded=False)
					with my_expander:

						fig, ax = plt.subplots(figsize=(15, 10))
						sns.countplot(y= df["indic_cat"])
						ax.set_title(" Dempographics followed by HIV/Aids most popular among the all! ")
						st.pyplot(fig)

						fig, ax = plt.subplots(figsize=(15, 10))
						sns.countplot(y= df["Race"])
						ax.set_title(" Most people with these indicators are the White, down to the Black, and the Hispanic ")
						st.pyplot(fig)

						fig, ax = plt.subplots(figsize=(10, 5))
						sns.countplot(y= df["Sex"])
						ax.set_title(" From the gender visualization, more people with the indicators are Females followed by the Males ")
						st.pyplot(fig)
		
			else:
				st.warning("Incorrect Username/Password")
	elif choice == "SignUp":
		st.subheader("Create New Account")
		new_user = st.text_input("Username")
		new_password = st.text_input("Password",type='password')

		if st.button("Signup"):
			create_usertable()
			data=user_exists(new_user)
			if data >0:
				st.warning("Username already exists !")
			else:
				add_userdata(new_user,make_hashes(new_password))
				st.success("You have successfully created a valid Account,Login in please!")


if __name__ == '__main__':
	main()



