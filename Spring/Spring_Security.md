
#### Spring Security :

 - https://docs.spring.io/spring-security/reference/servlet/authentication/architecture.html
 - https://medium.com/geekculture/spring-security-authentication-process-authentication-flow-behind-the-scenes-d56da63f04fa
 - https://www.baeldung.com/security-spring


 - <strong>Spring Security provides the following built in mechanisms for reading a username and password from the HttpServletRequest.</strong>


##### Authentication : 
 - Authentication is how we verify the identity of who is trying to access a particular resource. A common way to authenticate users is by requiring the user to enter a username and password.
##### Authorization : 
 - Authorization is a process by which a server determines if the client has permission to use a resource or access a file.

<table class="table"><thead>
<tr>
<th><strong>Authentication</strong></th>
<th><strong>Authorization</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>Determines whether users are who they claim to be</td>
<td>Determines what users can and cannot access</td>
</tr>
<tr>
<td>Challenges the user to validate credentials (for example, through passwords, answers to security questions, or facial recognition)</td>
<td>Verifies whether access is allowed through policies and rules</td>
</tr>
<tr>
<td>Usually done before authorization</td>
<td>Usually done after successful authentication</td>
</tr>
<tr>
<td>Generally, transmits info through an ID Token</td>
<td>Generally, transmits info through an <dfn id="react-containers-DefinitionTooltip-0"><span class="tooltip-portal-underlined-word">Access Token</span></dfn></td>
</tr>
<tr>
<td>Generally governed by the <dfn id="react-containers-DefinitionTooltip-1"><span class="tooltip-portal-underlined-word">OpenID Connect (OIDC) protocol</span></dfn></td>
<td>Generally governed by the OAuth 2.0 framework</td>
</tr>
<tr>
<td>Example: Employees in a company are required to authenticate through the network before accessing their company email</td>
<td>Example: After an employee successfully authenticates, the system determines what information the employees are allowed to access</td>
</tr>
</tbody>
</table>


#### Authentication Flow in spring security : 

![image](https://user-images.githubusercontent.com/31141888/164896664-f02cdb1d-2f33-4ab8-9abd-26acf61aeb55.png)
![image](https://user-images.githubusercontent.com/31141888/164896721-56e4ab72-3640-4c83-8deb-2d68f4563f44.png)


  - <strong>Step 1 :</strong> When the server receives a request for authentication, such as a login request, it is first intercepted by the Authentication Filter in the Filter Chain.
  - <strong>Step 2 :</strong> When the username and password are submitted, the `UsernamePasswordAuthenticationFilter` authenticates the username and password. The `UsernamePasswordAuthenticationFilter` creates a `UsernamePasswordAuthenticationToken` which is a type of Authentication by extracting the username and password from the `HttpServletRequest`.
  - <strong>Step 3 :</strong>  The `UsernamePasswordAuthenticationToken` is passed to the `AuthenticationManager` so that the token can be authenticated.
  - <strong>Step 4 :</strong>  The `AuthenticationManager` delegates the authentication to the appropriate `AuthenticationProvider`. 
  - <strong>Step 5 :</strong> The `AuthenticationProvider` calls the `loadUserByUsername(username)` method of the `UserDetailsService` and gets back the `UserDetails object` containing all the data of the user. The most important data is the password becuase it will be used to check whether the provided password is correct. If no user is found with the given user name, a `UsernameNotFoundException is thrown`.
  - <strong>Step 6 :</strong> The `AuthenticationProvider` after receiving the `UserDetails` checks the passwords and authenticates the user. If the passwords do not match it throws a `AuthenticationException`. However, if the authentication is successful, a `UsernamePasswordAuthenticationToken` is created, and the fields principal, credentials, and authenticated are set to appropriate values .
  - <strong>Step 7 :</strong>  On successful authentication, the `SecurityContext` is updated with the details of the current authenticated user. `SecurityContext` can be used in several parts of the app to check whether any user is currently authenticated and if so, what are the user’s details.

##### @EnableWebSecurity: This annotation enables Spring Security’s web security support to your application
```

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {
	@Autowired
	public void configureGlobal(AuthenticationManagerBuilder auth) throws Exception {
		auth.inMemoryAuthentication()
			.withUser("Dhiraj").password("{noop}d@123").roles("ADMIN")
			.and()
			.withUser("abc").password("{noop}a@123").roles("USER");
	}
	
	@Override
	protected void configure(HttpSecurity http) throws Exception {
		http.authorizeRequests()
		.antMatchers("/**").hasAnyRole("EMPLOYEE","USER")
			.anyRequest().authenticated()			
			.and().formLogin();					
	}
}

```
##### configureGlobal(AuthenticationManagerBuilder auth) only provides information about how to authenticate application users.

 - How does Spring Security know which requests to authenticate?
 - How does Spring Security know whether to support form-based or HTTP Basic authentication?
 - How to configure secure logout feature?
 - How to configure concurrent session management for restricting multiple sessions at a time?
 - How to configure URL based security which is to restrict the URL access to various roles?
 * All these types of required security features can be configured through the HttpSecurity of configure() method.

##### Spring Security helps us to prevent a user from concurrently accessing the application. SessionManagementFilter of Spring Security API handles this requirement and we can also specify how many numbers of sessions allowed per user through the below configuration.
```
http.sessionManagement().maximumSessions(1)

```

###### The below configuration code snippet enables Https protocol to be used for any request serviced by the web application.
```
http.requiresChannel().anyRequest()
			 .requiresSecure();

```

##### Remember Me Service :  Remember-me service helps the application to remember the user even after the browser is closed.
1. Token based remember-me service 
 - If the user has enabled the remember-me checkbox during authentication, then the application creates a cookie(username, expire time/date with Cookie signature details),  sends this cookie in its response to the client and which client (browser) will store it.

 - The browser will send the cookie along with the subsequent user requests to the application, Spring security will retrieve the user password details based on the cookie stored username with the help of the UserDetailsService of Authentication manager and generates the new cookie signature.

 - If the generated cookie signature and the client sent cookie signature are matching then it will allow the user to login without providing authentication. The remember me token is valid only till it reaches the expiration time or the user explicitly logout from the application.

2. Persistent based remember-me service 
 - In persistent based remember-me services, the user token is validated against the database.
 - When the user logs in with remember me checkbox enabled, application remember me functionality helps in generating a series identifier based on the user data. Also, a token which is a random value is also generated. The series and the token values are stored in the database persistent_logins table at the server end and also shared with the client in the response which will be stored as a cookie on the client browser.

 - For subsequent user requests to the application, the client sent the cookie with stored series and token values along with the user request to the server.

 - Spring security's remember-me functionality extracts the expiration and token values from the database table based on the arrived series identifier.

 - If the cookie token value matches with the token value retrieved from the database, then the user is logged in successfully and also

 	- The application will generate new token value and update this token value along with timestamp in the database table and also shares it with the client in the response which the client will store and will use it during subsequent request.

 	- So for every subsequent requests a new token value is generated, with the same series identifier till the user logs out or till the expiration time is reached.

#### Restricting URL ACCESS :
 ```
 http.authorizeRequests() 
		.antMatchers("/images/**").permitAll()
		.antMatchers("/login*").permitAll()
		.antMatchers("/report*").hasRole("EMPLOYEE") .anyRequest().authenticated()
		.antMatchers("/**").hasAnyRole("EMPLOYEE","USER")

 ```
 
  - Method level security  :
  	- From version 2.0 onwards, Spring Security started supporting security to your service layer methods. It has its original @Secured approach to secure methods  and also provides support for JSR-250 annotations such as @PreAuthorize, @PostAuthorize, etc. to support your methods.

	- Spring Security 3.0 introduced Spring Expression Language which can be used in authorization mechanisms to provide more restrictive access to the methods through powerful expression-based access control through annotations such as @PreAuthorize/@PostAuthorize.

```
@EnableGlobalMethodSecurity(secureEnabled = true) // To use @Secured 
                     OR
 
@EnableGlobalMethodSecurity(prePostEnabled = true) //To use @PreAuthorize

- @EnableGlobalMethodSecurity annotation has two important elements:

	1. securedEnabled: for enabling method level security using @Secured annotation

	2. prePostEnabled: for enabling method level security using @PreAuthorize and @PostAuthorize annotations
```

<table border="1" cellpadding="1" cellspacing="1" style="null">
	<thead>
		<tr>
			<th scope="col">
			<p style="null"><span style="null">Expression</span></p>
			</th>
			<th scope="col">
			<p style="null"><span style="null">Description</span></p>
			</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td>
			<p style="null"><span style="null">hasRole(role)</span></p>
			</td>
			<td>
			<p style="null"><span style="null">checks if the user has the role specified</span></p>
			</td>
		</tr>
		<tr>
			<td>
			<p style="null"><span style="null">hasAnyRole(role1,role2,..)</span></p>
			</td>
			<td>
			<p style="null"><span style="null">checks if the user has any of the roles specified</span></p>
			</td>
		</tr>
		<tr>
			<td>
			<p style="null"><span style="null">isRememberMe()</span></p>
			</td>
			<td>
			<p style="null"><span style="null">if the user is a remember-me enabled user then it returns true</span></p>
			</td>
		</tr>
		<tr>
			<td>
			<p style="null"><span style="null">isAuthenticated ()</span></p>
			</td>
			<td>
			<p style="null"><span style="null">if the user is authenticated then it returns true</span></p>
			</td>
		</tr>
		<tr>
			<td>
			<p style="null"><span style="null">isFullyAuthenticated()</span></p>
			</td>
			<td>
			<p style="null"><span style="null">the user has to be fully authenticated, he should not be anonymous or remember-me user</span></p>
			</td>
		</tr>
		<tr>
			<td>
			<p style="null"><span style="null">permitAll()</span></p>
			</td>
			<td>
			<p style="null"><span style="null">returns true and allows everyone to access</span></p>
			</td>
		</tr>
		<tr>
			<td>
			<p style="null"><span style="null">denyAll()</span></p>
			</td>
			<td>
			<p style="null"><span style="null">returns false and denies everyone to access</span></p>
			</td>
		</tr>
	</tbody>
</table>

<table border="1" cellpadding="1" cellspacing="1" style="null">
	<thead>
		<tr>
			<th scope="col">
			<p style="null"><span style="null">Expression</span></p>
			</th>
			<th scope="col">
			<p style="null"><span style="null">Description</span></p>
			</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td>
			<p style="null"><span style="null">@PreAuthorize</span></p>
			</td>
			<td>
			<p style="null"><span style="null">checks the authority of the user before invoking the method</span></p>
			</td>
		</tr>
		<tr>
			<td>
			<p style="null"><span style="null">@PostAuthorize</span></p>
			</td>
			<td>
			<p style="null"><span style="null">checks the authority of the user after executing the method</span></p>
			</td>
		</tr>
		<tr>
			<td>
			<p style="null"><span style="null">@PreFilter</span></p>
			</td>
			<td>
			<p style="null"><span style="null">helps to filter the input data which is a collection</span></p>
			</td>
		</tr>
		<tr>
			<td>
			<p style="null"><span style="null">@PostFilter</span></p>
			</td>
			<td>
			<p style="null"><span style="null">helps to filter the data on the returned collection</span></p>
			</td>
		</tr>
	</tbody>
</table>

###### Page Level Restriction :
 -we can make use of authorize tag from Spring Security tag library to provide page-level restriction wherein only the content relevant to the logged in role will be displayed in a controlled way.
 ```
 <security:authorize access="hasRole('ROLE_EMPLOYEE')">
    <a href="report.htm">Generate Report</a>
</security:authorize>

 ```
