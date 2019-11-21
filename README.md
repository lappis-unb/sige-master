# Sistema de Monitoramento de Insumos da Universidade de Brasília - S.M.I.

## About

The Sistema de Monitoramento de Insumos of the Universidade de Brasília (SMI-UnB), is a web application developed to assist in the monitoring and management of Universidade de Brasília's power consumption and distribution.

The idea is to monitor, collect and display data of each campus power supply, allowing a much better comprehension of the usage patterns and energy quality received from the distribution station.

The system is divided into three main layers:

- the presentation layer, which holds the front-end of the application, including the dashboard for researchers.
- the master layer, which is responsible for all the data management, data processing, and database redundancy.
- the slave layer is responsible for the communication with energy transductors and data collection.

## Installation

### Docker

First install Docker following the instructions according to your Operational System, [here](https://docs.docker.com/install/).

### Docker Compose

After installing Docker, you can install Docker-Compose, also according to your Operational System [here](https://docs.docker.com/compose/install/).

### Runnning SMI Master

If you have already lifted up [SMI Slave's API](https://gitlab.com/lappis-unb/projects/SMI/smi-slave). All you have to do is:

``` bash
sudo docker-compose up
```

If you haven't you must create the docker network needed for Master to connect. As:

``` bash
sudo docker network create smi-network
```

and you can lift up you Master environment with:

``` bash
sudo docker-compose up
```

And, that's it! You have SMI up and running!

### Running SMI Master Using Make

To simplify the commands you can use make to run the application. You can lift up you Master environment with:

``` bash
sudo make up
```

*****obs:******** This command creates the smi network if it doesn't exist yet.

#### Other commands

``` bash
sudo make stop # stop all Master containers
sudo make down # down all Master containers
sudo make dump # generate a dump with the saved data
sudo make loaddump # restore dumped data to dump-db.json file
sudo make fixhstore # fix hstore error
```


