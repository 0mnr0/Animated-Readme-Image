<p align="center">
 <h2 align="center">Animated Readme Image</h2>
 <p align="center">Get your animated readme image!</p>
</p>

> [!WARNING]
> <b> Restrictions </b> <br>
> The GitHub CDN does not allow you to insert images weighing more than 5mb, so far there is no way to circumvent this limitation.


> [!NOTE]
> The server will automatically update your image every 4 hours unless there are any errors. The server will remember the last arguments that you sent and will create them.

<p align="center"> 
  <h2 align="center"> HOW TO CREATE ONE? </h2>
</p>

### 1) Create a repository that will be called by your username on GitHub
<p> In my example, it's "0mnr0" (not dsvl0) </p> <br>

### 2) Create folder "files" in this repository:
<img width="302" height="218" alt="image" src="https://github.com/user-attachments/assets/d964557c-ffbb-4349-b982-f4772443484f" />
<br>
-------------------------------

### 3) Create "layout.html" file in new folder:
 <img width="304" height="262" alt="image" src="https://github.com/user-attachments/assets/66ea4c2c-1313-4d67-ba68-17816e3df5e6" />
<p> You can also place required files into that folder, for example "background.webm". </p>
<p> You are free to compose anything in the HTML file, there are no restrictions. It is advisable not to use any dependent "web components", work with them locally, or not add them at all. By "web components" I mean any libraries (For example, Bootstrap, Tailwind, jQuery and others that work through src="https://cdnjs.com/libraries /...") </p>

> [!WARNING]
> If you adding additionals files you need to specify full path to them. For example:<br>
> WILL NOT WORK: ```src="background.webm"```<br>
> THIS WORKS GREAT: ```src="https://github.com/0mnr0/0mnr0/raw/refs/heads/main/files/background.webm"```

### 4) Creating API
<br>

#### "/myReadme"
> Returning animated image with needed params

| Name | Description | Default value | Avaiable values |
| --- | --- | --- | --- |
| `person` | Get layout.html from spcified GitHub person | none | Any |
| `width` | Capturing an area ?px in width | auto | >= 1 |
| `height` | Capturing an area ?px in height | auto | >= 1 |
| `type` | Specify you need an animated or static image | video | ```image \| video \| none``` |
| `fps` | (CURRENTLY DISABLED). Specify max fps for animation (MAX: 24) | 24 | >= 1 |
| `nocache` | Disable cache to "recook" your layout file| false | ```true \| false \| none``` |
| `length` | length of your animation (min: 0s | max: 30s) | - | ```>0 & <30``` |
| `quality` | Specify the quality of the output file (JPG format) | 90 | ```>= 0 & <= 100``` |

> [!CAUTION]
> The ```nocache=true``` parameter will redirect to the "/reameStatus?person=..." page. It is useless to use this key in the readme, it will not return the image. This option is needed to test and create your animated readme.
<br>

#### "/readmeStatus"
> The readme status will be displayed within 30 seconds.

| Name | Description | Default value | Avaiable values |
| --- | --- | --- | --- |
| `person` | Get current status of persons readme image | none | Any |

<br>

#### "/myReadmeSize"
> Displaying current readme size (MB and bytes).

| Name | Description | Default value | Avaiable values |
| --- | --- | --- | --- |
| `person` | Get current readme image size | none | Any |
