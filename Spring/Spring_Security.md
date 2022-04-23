
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
