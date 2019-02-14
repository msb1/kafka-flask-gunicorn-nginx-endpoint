### kafka-flask-gunicorn-nginx-tester

<h4> General Info </h4>
<ol>
  <li> 
    The purpose of this application is enable a Kafka endpoint simulator for testing Kafka, Kafka Connect and Kafka Streams with simulated analytics data streams
  </li>
  <li>
    In this test application, kafka-python is used to spawn a producer and consumer which are each enabled in a separate classes that inherit threading.Thread 
    <ul>
      <li> Currently the producer and consumer are set to bootstrap_servers='localhost:9092. Change the following lines to enable different kafka brokers. </li>
      <li> self.consumer = KafkaConsumer(topic, bootstrap_servers='localhost:9092', consumer_timeout_ms=1000) </li>
      <li> self.producer = KafkaProducer(bootstrap_servers='localhost:9092') </li>
      <li> The default topic is current set to 'sim-test'. This should be changed as well to suit the needs of the application
    </ul>
  </li>
  <li>
    These classes are instantiated when the Flask application begins and the threads are closed/joined when the application (or web page) is closed
  </li>
  <li> 
    The web page is based on the bootstrap sample dashboard from https://startbootstrap.com/previews/sb-admin-2/ so there is considerable flexibility in its application. There are currently a start and stop button in the left-side collapsable menu.
  </li>
  <li> 
    flask-socketio provides access to low latency bi-directional communications between the client web page and the server. The client-side application uses javascript Socket.io
  </li>
</ol>

<h4>Server Info </h4>
<ol>
  <li>
    Gunicorn is used as the WSGI HTTP server to run flask app - testkafka.py. As this app utilizes flask-socketio, the gevent worker is also needed. The following is included in the docker-compose.yml file to start the Gunicorn server with the gevent worker.
  </li>
  <li>
    command: gunicorn -k gevent -w 1 -b :8000 testkafka:app 
  </li>
  <li>
    Nginx is set up as reverse proxy server to the Gunicorn server running on localhost port 8000
  </li>
  <li>
    The guidelines for setting up the Nginx server with Gunicorn are taken from http://docs.gunicorn.org/en/stable/deploy.html#nginx-configuration and http://pawamoy.github.io/2018/02/01/docker-compose-django-postgres-nginx.html. These are reflected in the nginx.conf file.
  </li>
</ol>

<h4> Docker Info </h4>
<ol>
  <li>
    docker-compose is used to build the docker images. Four images are built with the docker-compose.yml included with this application including
      <ul>
        <li> flask-kafka-tester_testapp</li>
        <li> flask-kafka-tester-nginx</li>
        <li> nginx </li>
        <li> continuumio/miniconda3
      </ul>   
  </li>
  <li>
    The structure of the docker-compose.yml is based on http://www.ameyalokare.com/docker/2017/09/20/nginx-flask-postgres-docker-compose.html 
  </li>
  <li>
    miniconda3 from continuum is used for the base python environment. The inherited docker image used for miniconda3 is built with debian
  </li>
  <li>
    miniconda3 is used since this application is intended for analytics simulating and testing. The conda installer is very good at resolving dependencies used in machine and deep learning.
  </li>
  <li>
    miniconda3 is a bare python3.7 environment with the conda installer. Care should be exercised to include the appropriate repos for the python dependencies needed for the application. In the testapp dockerfile, two separate conda installs are made to resolve dependencies from the anaconda and conda-forge repos
  </li>
</ol>

<h5> This application is highly configurable. The code and config outlined here is a basic example of potential possibilities. Best wishes... </h5>
