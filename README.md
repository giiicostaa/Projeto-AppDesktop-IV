# VetCare — Sistema de Clínica Veterinária (Nível 4)

## Descrição

O **VetCare** é um sistema de gerenciamento de clínica veterinária desenvolvido em Python utilizando Programação Orientada a Objetos (POO), banco de dados **SQLite** e **interface gráfica com Tkinter**.

Esta versão corresponde ao **Nível 4** da atividade, reunindo todos os recursos dos níveis anteriores e acrescentando uma interface gráfica para facilitar a utilização do sistema.

---

# Funcionalidades

O sistema permite:

- Cadastro de clientes;
- Cadastro de veterinários;
- Cadastro de animais;
- Associação de animais aos seus tutores;
- Agendamento de consultas;
- Edição de registros;
- Exclusão de registros;
- Conclusão e cancelamento de consultas;
- Listagem completa dos cadastros;
- Relatório geral da clínica;
- Teste de polimorfismo;
- Persistência dos dados em banco SQLite;
- Interface gráfica amigável.

---

# Conceitos de POO

## Classes Abstratas

- Pessoa
- Animal

## Herança

- Cliente → Pessoa
- Veterinario → Pessoa
- Cachorro → Animal
- Gato → Animal

## Polimorfismo

O método `emitir_som()` possui implementações diferentes para cada animal.

## Associação

A classe `Consulta` relaciona:

- Cliente
- Animal
- Veterinário

## Composição

A classe principal gerencia clientes, veterinários, animais e consultas.

## Dependência

As classes trabalham em conjunto para realizar todas as operações do sistema.

---

# Interface gráfica

A aplicação utiliza **Tkinter**, biblioteca gráfica padrão do Python.

A interface possui:

- Janela principal;
- Abas para Clientes;
- Abas para Veterinários;
- Abas para Animais;
- Abas para Consultas;
- Tabelas (Treeview);
- Botões de cadastro, edição, exclusão e atualização;
- Formulários para inserção de dados;
- Caixas de diálogo para avisos e confirmações.

---

# Banco de Dados

O sistema utiliza SQLite.

Na primeira execução é criado automaticamente:

```text
vetcare.db
```

São criadas automaticamente as tabelas:

- clientes
- veterinarios
- animais
- consultas

O banco utiliza:

- PRIMARY KEY
- FOREIGN KEY
- ON DELETE CASCADE
- restrições de unicidade para CPF e CRMV.

---

# Tecnologias utilizadas

- Python 3
- Tkinter
- SQLite (sqlite3)
- abc

Todas fazem parte da biblioteca padrão do Python.

---

# Estrutura do projeto

```text
Pessoa (Classe Abstrata)
├── Cliente
└── Veterinario

Animal (Classe Abstrata)
├── Cachorro
└── Gato

Consulta

BancoDados

Interface Gráfica (Tkinter)

Aplicação Principal
```

---

# Relatório

O sistema apresenta um relatório contendo:

- quantidade de clientes;
- quantidade de veterinários;
- quantidade de animais;
- consultas agendadas;
- consultas concluídas;
- consultas canceladas.

---

# Persistência dos dados

Os dados permanecem armazenados no arquivo **vetcare.db**, mesmo após o encerramento da aplicação.

---

# Requisitos

- Python 3.8 ou superior.

Não é necessário instalar bibliotecas externas.

---


# Autor

Projeto acadêmico desenvolvido para atender aos requisitos do **Nível 4**, integrando Programação Orientada a Objetos, banco de dados SQLite e interface gráfica em Python
realizado pelas alunas: Giovanna da Costa Santos (251021303) e Geovana Duarte de Carvalho (251021241).
