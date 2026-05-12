package com.iset.Agent.config;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {

    public static final String QUEUE_TICKET_RESOLVED = "ticket.resolved.queue";
    public static final String EXCHANGE = "reclamations.exchange";
    public static final String ROUTING_RESOLVED = "ticket.resolved";

    @Bean
    public Queue ticketResolvedQueue() {
        return new Queue(QUEUE_TICKET_RESOLVED, true);
    }

    @Bean
    public TopicExchange exchange() {
        return new TopicExchange(EXCHANGE);
    }

    @Bean
    public Binding binding(Queue ticketResolvedQueue, TopicExchange exchange) {
        return BindingBuilder.bind(ticketResolvedQueue).to(exchange).with(ROUTING_RESOLVED);
    }

    @Bean
    public Jackson2JsonMessageConverter messageConverter() {
        return new Jackson2JsonMessageConverter();
    }

    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory) {
        RabbitTemplate template = new RabbitTemplate(connectionFactory);
        template.setMessageConverter(messageConverter());
        return template;
    }
}